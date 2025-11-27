from django.conf import settings as django_settings
from content.models import ContentSource, ContentChunk
from .models import Quiz, Question
from typing import List, Dict, Any
import requests
import logging
import json

class DeepseekError(Exception):
    """Custom error type for DeepSeek API problems."""
    pass

def collect_chunks(contents: List[ContentSource]) -> List[Dict[str, Any]]:
    if not contents:
        return []

    content_ids = [c.id for c in contents]

    chunks_qs = (
        ContentChunk.objects
        .filter(content_id__in=content_ids)
        .order_by("content_id", "index")
    )

    chunks: List[Dict[str, Any]] = []
    for ch in chunks_qs:
        chunks.append(
            {
                "content_id": ch.content_id,
                "content_title": ch.content.title if ch.content_id else "",
                "index": ch.index,
                "text": ch.text or "",
            }
        )
    return chunks

def _dummy_generate_quiz(
    quiz_title: str,
    settings: dict,
    contents: List[ContentSource],
    chunks: List[Dict[str, Any]],
    user_instructions: str = "",
) -> Dict[str, Any]:
    if settings is None:
        settings = {}

    num_questions = int(settings.get("num_questions", 5) or 5)
    question_types = settings.get("question_types") or ["MCQ"]
    difficulty = settings.get("difficulty", "medium") or "medium"
    bloom_level = settings.get("bloom_level", "understand") or "understand"

    if not chunks:
        chunks = [
            {
                "content_id": None,
                "content_title": quiz_title,
                "index": 1,
                "text": "No content text was available. This is placeholder content.",
            }
        ]

    questions: List[Dict[str, Any]] = []

    for i in range(1, num_questions + 1):
        q_type = question_types[(i - 1) % len(question_types)] or "MCQ"
        chunk = chunks[(i - 1) % len(chunks)]
        context_snippet = (chunk.get("text") or "")[:400]
        content_title = chunk.get("content_title") or "Your content"

        prompt = (
            f"Based on the following study material, answer the question.\n\n"
            f"Context (from '{content_title}'):\n"
            f"{context_snippet}\n\n"
            f"Question {i}: Summarize or answer a key idea from this context."
        )

        q_data: Dict[str, Any] = {
            "index": i,
            "type": q_type,
            "prompt": prompt,
            "difficulty": difficulty,
            "bloom_level": bloom_level,
            "metadata": {},
        }

        if q_type == "MCQ":
            q_data["correct_answer"] = "A"
            q_data["explanation"] = (
                "This is a placeholder explanation. In a real system, "
                "the explanation would describe why the correct option is right."
            )
            q_data["choices"] = [
                {"label": "A", "text": "Correct placeholder answer based on the context."},
                {"label": "B", "text": "A plausible but incorrect option."},
                {"label": "C", "text": "Another distractor option."},
                {"label": "D", "text": "Yet another distractor option."},
            ]
        else:
            q_data["correct_answer"] = "Sample ideal answer based on the context."
            q_data["explanation"] = (
                "This is a placeholder explanation for a non-MCQ question, "
                "describing what a good answer should contain."
            )
            q_data["choices"] = []

        questions.append(q_data)

    quiz_json: Dict[str, Any] = {
        "title": quiz_title,
        "settings": settings,
        "questions": questions,
    }
    return quiz_json

logger = logging.getLogger(__name__)

class DeepseekError(Exception):
    """Custom error type for DeepSeek API problems."""
    pass


def generate_quiz_via_deepseek(
    quiz_title: str,
    settings: dict,
    contents: List[ContentSource],
    chunks: List[Dict[str, Any]],
    user_instructions: str = "",
) -> Dict[str, Any]:

    api_key = getattr(django_settings, "DEEPSEEK_API_KEY", None)

    # If you REALLY never want dummy, you can also raise here instead
    if not api_key:
        raise DeepseekError("DEEPSEEK_API_KEY is not set on the server")

    # Keep context reasonable but you can adjust this up/down
    if not chunks:
        merged_text = "No content provided."
    else:
        merged_text = "\n".join(
            (c["text"] or "")[:900]    # up to 900 chars per chunk
            for c in chunks[:6]        # up to 6 chunks
        )

    system_prompt = (
        "You are an AI that generates QUIZ QUESTIONS ONLY in VALID JSON.\n"
        "Rules:\n"
        "- Output MUST be valid JSON only (no markdown, no comments, no ```)\n"
        "- Follow the given schema strictly.\n"
        "- Questions should be challenging but fair, based on the given context.\n"
    )

    user_prompt = {
        "quiz_title": quiz_title,
        "instructions": user_instructions,
        "settings": settings,
        "context": merged_text,
        "schema": {
            "title": "string",
            "settings": "same as input 'settings'",
            "questions": [
                {
                    "index": "integer (1-based)",
                    "type": "MCQ | FRQ | TRUE_FALSE | CLOZE | MATCHING | REASONING",
                    "prompt": "non-empty string, clear standalone question",
                    "difficulty": "easy | medium | hard",
                    "bloom_level": "e.g. remember, understand, apply, analyze, evaluate, create",
                    "correct_answer": "string (for MCQ = label like 'A')",
                    "choices": [
                        {"label": "A", "text": "string"},
                        {"label": "B", "text": "string"},
                        {"label": "C", "text": "string"},
                        {"label": "D", "text": "string"},
                    ],
                    "explanation": "string (why the answer is correct)",
                    "metadata": "optional object",
                }
            ],
        },
    }

    try:
        resp = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": json.dumps(user_prompt)},
                ],
                "temperature": 0.3,
                "response_format": {"type": "json_object"},
            },
            timeout=180,  # ⏱ give DeepSeek up to 3 minutes
        )
        resp.raise_for_status()
    except requests.exceptions.Timeout as e:
        logger.error("DeepSeek timeout: %s", e)
        raise DeepseekError(f"DeepSeek request timed out after 180s: {e}")
    except requests.exceptions.RequestException as e:
        logger.error("DeepSeek HTTP error: %s", e)
        raise DeepseekError(f"DeepSeek HTTP error: {e}")

    try:
        data = resp.json()
    except ValueError as e:
        logger.error("DeepSeek returned non-JSON: %s / body=%s", e, resp.text[:300])
        raise DeepseekError(f"Failed to parse DeepSeek JSON: {e}")

    try:
        content = data["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error("DeepSeek unexpected response format: %s / data=%s", e, str(data)[:300])
        raise DeepseekError(f"Unexpected DeepSeek response format: {e}")

    # DeepSeek with response_format=json_object may give dict or string
    if isinstance(content, dict):
        quiz_json = content
    else:
        try:
            quiz_json = json.loads(content)
        except json.JSONDecodeError as e:
            logger.error("DeepSeek content not JSON: %s / content=%s", e, str(content)[:300])
            raise DeepseekError(f"DeepSeek returned non-JSON content: {e}")

    if "questions" not in quiz_json or not isinstance(quiz_json["questions"], list):
        raise DeepseekError("DeepSeek JSON has no valid 'questions' list")

    return quiz_json

def save_quiz_from_json(quiz: Quiz, quiz_json: Dict[str, Any]) -> None:
    if quiz_json is None:
        quiz_json = {}

    quiz.output_json = quiz_json
    quiz.save()

    quiz.questions.all().delete()

    for q_data in quiz_json.get("questions", []):
        question = Question.objects.create(
            quiz=quiz,
            index=q_data.get("index") or 0,
            type=q_data.get("type") or "MCQ",
            prompt=q_data.get("prompt") or "",
            difficulty=q_data.get("difficulty") or "",
            bloom_level=q_data.get("bloom_level") or "",
            correct_answer=q_data.get("correct_answer") or "",
            explanation=q_data.get("explanation") or "",
            metadata=q_data.get("metadata") or {},
        )

        for choice_data in q_data.get("choices") or []:
            label = choice_data.get("label") or ""
            text = choice_data.get("text") or ""
            is_correct = (label == question.correct_answer)
            question.choices.create(
                label=label,
                text=text,
                is_correct=is_correct,
            )

def regenerate_question_via_deepseek(
    question: Question,
    quiz: Quiz,
    contents: List[ContentSource],
    chunks: List[Dict[str, Any]],
    overrides: Dict[str, Any] | None = None,
    user_instructions: str = "",
) -> Dict[str, Any]:

    overrides = overrides or {}
    api_key = getattr(django_settings, "DEEPSEEK_API_KEY", None)

    if not api_key:
        print("⚠️ No DEEPSEEK_API_KEY – using dummy question regeneration.")
        return _dummy_regenerate_question(question, chunks, overrides)

    if chunks:
        context_snippet = (chunks[0].get("text") or "")[:800]
    else:
        context_snippet = "No context available, rely on the question text."

    q_type = overrides.get("type") or question.type or "MCQ"
    difficulty = overrides.get("difficulty") or question.difficulty or "medium"
    bloom_level = overrides.get("bloom_level") or question.bloom_level or ""

    system_prompt = (
        "You are an AI that REGENERATES a single quiz question.\n"
        "You must output ONLY valid JSON for ONE question object.\n"
        "No markdown, no comments, no explanations. Just JSON.\n"
    )

    user_payload = {
        "original_question": {
            "type": question.type,
            "prompt": question.prompt,
            "difficulty": question.difficulty,
            "bloom_level": question.bloom_level,
            "correct_answer": question.correct_answer,
            "choices": [
                {"label": c.label, "text": c.text, "is_correct": c.is_correct}
                for c in question.choices.all().order_by("label")
            ],
            "explanation": question.explanation,
        },
        "quiz_settings": quiz.settings,
        "overrides": {
            "type": q_type,
            "difficulty": difficulty,
            "bloom_level": bloom_level,
        },
        "user_instructions": user_instructions,
        "context_snippet": context_snippet,
        "schema": {
            "index": f"{question.index} (keep same index)",
            "type": "MCQ | FRQ | TRUE_FALSE | CLOZE | MATCHING | REASONING",
            "prompt": "new, clear standalone question",
            "difficulty": "string",
            "bloom_level": "string",
            "correct_answer": "string (for MCQ = label like 'A')",
            "choices": [
                {"label": "A", "text": "string"},
                {"label": "B", "text": "string"},
                {"label": "C", "text": "string"},
                {"label": "D", "text": "string"},
            ],
            "explanation": "string",
            "metadata": "optional object",
        },
    }

    try:
        resp = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": json.dumps(user_payload)},
                ],
                "temperature": 0.4,
                "response_format": {"type": "json_object"},
            },
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        q_json = json.loads(content)

        q_json.setdefault("index", question.index)
        return q_json

    except Exception as e:
        print("❌ DeepSeek regenerate failed, using dummy:", e)
        return _dummy_regenerate_question(question, chunks, overrides)


def _dummy_regenerate_question(
    question: Question,
    chunks: List[Dict[str, Any]],
    overrides: Dict[str, Any],
) -> Dict[str, Any]:
    q_type = overrides.get("type") or question.type or "MCQ"
    difficulty = overrides.get("difficulty") or question.difficulty or "medium"
    bloom_level = overrides.get("bloom_level") or question.bloom_level or ""

    context_snippet = ""
    if chunks:
        context_snippet = (chunks[0].get("text") or "")[:400]

    new_prompt = (
        f"(Regenerated) Based on this context:\n{context_snippet}\n\n"
        f"Provide a new question testing the same concept."
    )

    q_json: Dict[str, Any] = {
        "index": question.index,
        "type": q_type,
        "prompt": new_prompt,
        "difficulty": difficulty,
        "bloom_level": bloom_level,
        "correct_answer": "A" if q_type == "MCQ" else "Sample regenerated answer.",
        "explanation": (
            "This is a regenerated placeholder explanation. "
            "In a real system, this would be produced by an LLM."
        ),
        "metadata": {},
    }

    if q_type == "MCQ":
        q_json["choices"] = [
            {"label": "A", "text": "New correct placeholder answer."},
            {"label": "B", "text": "New distractor option 1."},
            {"label": "C", "text": "New distractor option 2."},
            {"label": "D", "text": "New distractor option 3."},
        ]
    else:
        q_json["choices"] = []

    return q_json


def explain_question_via_deepseek(
    question: Question,
    quiz: Quiz,
    contents: List[ContentSource],
    chunks: List[Dict[str, Any]],
) -> str:

    api_key = getattr(django_settings, "DEEPSEEK_API_KEY", None)

    if not api_key:
        print("⚠️ No DEEPSEEK_API_KEY – using dummy explanation.")
        return _dummy_explain_question(question, chunks)

    if chunks:
        context_snippet = (chunks[0].get("text") or "")[:600]
    else:
        context_snippet = "No extra source context is available."

    system_prompt = (
        "You are an AI that explains quiz questions to students.\n"
        "You MUST return ONLY valid JSON with one key: 'explanation'.\n"
        "No markdown, no backticks, no comments.\n"
    )

    user_payload = {
        "question": {
            "prompt": question.prompt,
            "type": question.type,
            "difficulty": question.difficulty,
            "bloom_level": question.bloom_level,
            "correct_answer": question.correct_answer,
            "choices": [
                {"label": c.label, "text": c.text, "is_correct": c.is_correct}
                for c in question.choices.all().order_by("label")
            ],
        },
        "quiz_settings": quiz.settings,
        "context_snippet": context_snippet,
    }

    try:
        resp = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": json.dumps(user_payload)},
                ],
                "temperature": 0.4,
                "response_format": {"type": "json_object"},
            },
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        obj = json.loads(content)

        explanation = obj.get("explanation", "").strip()
        if not explanation:
            raise ValueError("Empty explanation from DeepSeek.")
        return explanation

    except Exception as e:
        print("❌ DeepSeek explanation failed, using dummy:", e)
        return _dummy_explain_question(question, chunks)


def _dummy_explain_question(
    question: Question,
    chunks: List[Dict[str, Any]],
) -> str:
    context_snippet = ""
    if chunks:
        context_snippet = (chunks[0].get("text") or "")[:200]

    explanation = (
        "This is a placeholder explanation for the question. "
        "In a real system, this would reference the key ideas from the source content. "
        f"Example context snippet: {context_snippet}"
    )
    return explanation
