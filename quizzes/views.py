import json
import csv
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from content.models import ContentSource
from .models import Quiz, Question
from .serializers import QuizSerializer, QuizCreateSerializer, QuestionSerializer
from .services import (
    collect_chunks,
    generate_quiz_via_deepseek,
    save_quiz_from_json,
    regenerate_question_via_deepseek,
    explain_question_via_deepseek,
    DeepseekError,
)

def ping(request):
    return JsonResponse({"status": "ok", "message": "quizzes app is wired correctly"})



@api_view(["GET"])
def list_quizzes(request):
    quizzes = Quiz.objects.all().order_by("-created_at")[:50]
    serializer = QuizSerializer(quizzes, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def retrieve_quiz(request, pk):
    try:
        quiz = Quiz.objects.get(pk=pk)
    except Quiz.DoesNotExist:
        return Response(
            {"detail": "Quiz not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = QuizSerializer(quiz)
    return Response(serializer.data)

@csrf_exempt
@api_view(["POST"])
def create_quiz(request):
    serializer = QuizCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    validated = serializer.validated_data

    title = validated["title"]
    content_ids = validated["content_ids"]
    settings = validated["settings"]
    custom_instructions = validated.get("custom_instructions", "")

    contents = list(ContentSource.objects.filter(id__in=content_ids))
    if not contents:
        return Response(
            {"detail": "No valid content found for given content_ids."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    not_ready = [c.id for c in contents if c.status != ContentSource.Status.READY]
    if not_ready:
        return Response(
            {
                "detail": "Some content sources are not ready yet.",
                "not_ready_ids": not_ready,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    quiz = Quiz.objects.create(
        title=title,
        settings=settings,
        custom_instructions=custom_instructions,
        status=Quiz.Status.PROCESSING,
    )
    quiz.contents.set(contents)

    try:
        chunks = collect_chunks(contents)

        quiz_json = generate_quiz_via_deepseek(
            quiz_title=title,
            settings=settings,
            contents=contents,
            chunks=chunks,
            user_instructions=custom_instructions,
        )

        save_quiz_from_json(quiz, quiz_json)

        quiz.status = Quiz.Status.READY
        quiz.save()

    except DeepseekError as e:
        # ❗ DeepSeek-specific failure
        quiz.status = Quiz.Status.FAILED
        quiz.error_message = str(e)
        quiz.save()
        return Response(
            {"detail": "Quiz generation failed due to DeepSeek error.", "error": str(e)},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        quiz.status = Quiz.Status.FAILED
        quiz.error_message = str(e)
        quiz.save()
        return Response(
            {"detail": "Failed to generate quiz", "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    output_serializer = QuizSerializer(quiz)
    return Response(output_serializer.data, status=status.HTTP_201_CREATED)

@csrf_exempt
@api_view(["POST"])
def regenerate_question(request, quiz_id, question_id):
    try:
        quiz = Quiz.objects.get(pk=quiz_id)
    except Quiz.DoesNotExist:
        return Response({"detail": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)

    try:
        question = quiz.questions.get(pk=question_id)
    except Question.DoesNotExist:
        return Response(
            {"detail": "Question not found in this quiz"},
            status=status.HTTP_404_NOT_FOUND,
        )

    overrides = request.data or {}
    extra_instructions = overrides.pop("extra_instructions", "")

    contents = list(quiz.contents.all())
    chunks = collect_chunks(contents)

    try:
        q_json = regenerate_question_via_deepseek(
            question=question,
            quiz=quiz,
            contents=contents,
            chunks=chunks,
            overrides=overrides,
            user_instructions=(quiz.custom_instructions or "") + "\n" + extra_instructions,
        )

        question.type = q_json.get("type", question.type)
        question.prompt = q_json.get("prompt", question.prompt)
        question.bloom_level = q_json.get("bloom_level") or ""
        question.difficulty = q_json.get("difficulty") or question.difficulty
        question.explanation = q_json.get("explanation") or question.explanation
        question.correct_answer = q_json.get("correct_answer") or question.correct_answer
        question.metadata = {
            "matching_pairs": q_json.get("matching_pairs"),
            **(q_json.get("metadata") or {}),
        }

        question.choices.all().delete()
        if q_json.get("choices"):
            for choice_data in q_json["choices"]:
                label = choice_data.get("label", "")
                text = choice_data.get("text", "")
                is_correct = (label == q_json.get("correct_answer"))
                question.choices.create(
                    label=label,
                    text=text,
                    is_correct=is_correct,
                )

        question.save()

    except Exception as e:
        return Response(
            {"detail": "Failed to regenerate question", "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    serializer = QuestionSerializer(question)
    return Response(serializer.data)

@csrf_exempt
@api_view(["POST"])
def explain_question(request, quiz_id, question_id):
    try:
        quiz = Quiz.objects.get(pk=quiz_id)
    except Quiz.DoesNotExist:
        return Response({"detail": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)

    try:
        question = quiz.questions.get(pk=question_id)
    except Question.DoesNotExist:
        return Response(
            {"detail": "Question not found in this quiz"},
            status=status.HTTP_404_NOT_FOUND,
        )

    contents = list(quiz.contents.all())
    chunks = collect_chunks(contents)

    try:
        explanation = explain_question_via_deepseek(
            question=question,
            quiz=quiz,
            contents=contents,
            chunks=chunks,
        )
        question.explanation = explanation
        question.save()
    except Exception as e:
        return Response(
            {"detail": "Failed to generate explanation", "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    serializer = QuestionSerializer(question)
    return Response(serializer.data)

@api_view(["GET"])
def export_quiz_json(request, pk):
    try:
        quiz = Quiz.objects.get(pk=pk)
    except Quiz.DoesNotExist:
        return Response({"detail": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)

    data = quiz.output_json or {}

    response = HttpResponse(
        json.dumps(data, ensure_ascii=False, indent=2),
        content_type="application/json",
    )
    filename = f"quiz_{quiz.id}.json"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response



@api_view(["GET"])
def export_quiz_csv(request, pk):
    try:
        quiz = Quiz.objects.get(pk=pk)
    except Quiz.DoesNotExist:
        return Response({"detail": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)

    response = HttpResponse(content_type="text/csv")
    filename = f"quiz_{quiz.id}.csv"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(["index", "type", "prompt", "choices", "correct_answer", "explanation"])

    for q in quiz.questions.all().order_by("index"):
        if q.type == "MCQ":
            choices_str = "; ".join(
                f"{c.label}) {c.text}" for c in q.choices.all().order_by("label")
            )
        else:
            choices_str = ""

        writer.writerow([
            q.index,
            q.type,
            q.prompt,
            choices_str,
            q.correct_answer,
            q.explanation,
        ])

    return response