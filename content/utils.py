from urllib.parse import urlparse, parse_qs
from typing import List
import os
import requests
from django.conf import settings
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\Deniz Jafarzade\Desktop\HKU\Lessons\CCAI9024\ai_quiz_platform\tesseract\tesseract.exe"
from PIL import Image
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import tempfile

def clean_text(text: str) -> str:
    if not text:
        return ""
    import re
    text = text.replace("\r", " ").replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def simple_chunk_text(text: str, max_chars: int = 1000) -> List[str]:

    chunks = []
    current = []

    for word in text.split():
        current_len = sum(len(w) for w in current) + max(0, len(current) - 1)
        if current_len + 1 + len(word) > max_chars:
            chunks.append(" ".join(current))
            current = [word]
        else:
            current.append(word)

    if current:
        chunks.append(" ".join(current))

    return chunks

def extract_video_id(youtube_url: str) -> str:
    parsed = urlparse(youtube_url)
    if parsed.netloc in ("youtu.be", "www.youtu.be"):
        return parsed.path.lstrip("/")

    qs = parse_qs(parsed.query)
    if "v" in qs:
        return qs["v"][0]

    return parsed.path.split("/")[-1]


def fetch_youtube_transcript(youtube_url: str, language: str = "en") -> str:
    video_id = extract_video_id(youtube_url)

    lang_candidates = [language]
    if language != "en":
        lang_candidates.append("en")

    try:
        transcript = YouTubeTranscriptApi().fetch(video_id)
        text = " ".join(chunk.text for chunk in transcript)
        return text.strip()

    except TranscriptsDisabled:
        raise RuntimeError("Transcripts are disabled for this video.")
    except NoTranscriptFound:
        raise RuntimeError("No transcript found for this video in the requested languages.")
    except Exception as e:
        raise RuntimeError(f"Failed to fetch YouTube transcript: {e}")

def transcribe_audio_with_elevenlabs(
    file_obj_or_path,
    language: str = "",
) -> str:

    api_key = getattr(settings, "ELEVENLABS_API_KEY", None)
    if not api_key:
        raise RuntimeError("ELEVENLABS_API_KEY is not set in Django settings.")

    model_id = getattr(settings, "ELEVENLABS_STT_MODEL", "scribe_v2")

    url = "https://api.elevenlabs.io/v1/speech-to-text"

    temp_path = None

    # ✅ Support both Django UploadedFile and plain file paths
    if isinstance(file_obj_or_path, (str, bytes, os.PathLike)):
        file_path = file_obj_or_path
    else:
        # Assume it's a Django UploadedFile or file-like object
        suffix = os.path.splitext(getattr(file_obj_or_path, "name", "audio"))[1] or ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            if hasattr(file_obj_or_path, "chunks"):
                for chunk in file_obj_or_path.chunks():
                    tmp.write(chunk)
            else:
                tmp.write(file_obj_or_path.read())
            temp_path = tmp.name
        file_path = temp_path

    try:
        with open(file_path, "rb") as f:
            files = {
                "file": (os.path.basename(file_path), f, "application/octet-stream"),
            }
            data = {
                "model_id": model_id,
            }
            if language:
                data["language_code"] = language

            headers = {
                "xi-api-key": api_key,
            }

            response = requests.post(url, headers=headers, files=files, data=data, timeout=120)

        if response.status_code != 200:
            raise RuntimeError(
                f"ElevenLabs STT failed with status {response.status_code}: {response.text}"
            )

        try:
            payload = response.json()
        except Exception as e:
            raise RuntimeError(f"Failed to parse ElevenLabs STT response: {e}")

        transcript_text = payload.get("text") or payload.get("transcript")
        if not transcript_text:
            raise RuntimeError(f"ElevenLabs STT returned no transcript field: {payload}")

        return clean_text(transcript_text)

    finally:
        # clean up temp file if we created one
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

def extract_text_from_pdf_text_layer(pdf_path: str) -> str:
    text_chunks = []
    with open(pdf_path, "rb") as f:
        reader = PdfReader(f)
        for page in reader.pages:
            try:
                page_text = page.extract_text() or ""
            except Exception:
                page_text = ""
            if page_text:
                text_chunks.append(page_text)
    return clean_text(" ".join(text_chunks))


def pdf_to_images(pdf_path: str, dpi: int = 300, poppler_path: str | None = None) -> List[Image.Image]:
    images = convert_from_path(pdf_path, dpi=dpi, poppler_path=poppler_path)
    return images


def preprocess_image_for_ocr(image: Image.Image) -> Image.Image:
    img = image.convert("L")
    img = img.point(lambda x: 0 if x < 140 else 255, "L")

    w, h = img.size
    if w < 800:
        scale = 800 / w
        img = img.resize((int(w * scale), int(h * scale)))

    return img


def ocr_image(image: Image.Image, language: str = "eng") -> str:
    config = "--psm 6"
    raw_text = pytesseract.image_to_string(image, lang=language, config=config)
    return clean_text(raw_text)


def extract_text_from_pdf(pdf_path: str, language: str = "eng", poppler_path: str | None = None) -> str:
    text_from_layer = extract_text_from_pdf_text_layer(pdf_path)

    if len(text_from_layer) > 500:
        return text_from_layer

    images = pdf_to_images(pdf_path, dpi=300, poppler_path=poppler_path)
    ocr_chunks = []
    for img in images:
        preprocessed = preprocess_image_for_ocr(img)
        page_text = ocr_image(preprocessed, language=language or "eng")
        if page_text:
            ocr_chunks.append(page_text)

    return clean_text(" ".join(ocr_chunks))


def extract_text_from_image_file(image_path: str, language: str = "eng") -> str:
    img = Image.open(image_path)
    preprocessed = preprocess_image_for_ocr(img)
    text = ocr_image(preprocessed, language=language or "eng")
    return text
