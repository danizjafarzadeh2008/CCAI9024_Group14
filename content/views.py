from django.http import JsonResponse
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

from .models import ContentSource, ContentChunk
from .serializers import (
    ContentSourceSerializer,
    YouTubeContentCreateSerializer,
    AudioContentCreateSerializer,
    DocumentContentCreateSerializer,
)

import logging


from .utils import (
    simple_chunk_text,
    fetch_youtube_transcript,
    clean_text,
    transcribe_audio_with_elevenlabs,
    extract_text_from_pdf,
    extract_text_from_image_file,
)


def ping(request):
    return JsonResponse({"status": "ok", "message": "content app is wired correctly"})


@api_view(["GET"])
def list_content(request):
    contents = ContentSource.objects.all().order_by("-created_at")[:50]
    serializer = ContentSourceSerializer(contents, many=True, context={"request": request})
    return Response(serializer.data)


@api_view(["POST"])
def create_youtube_content(request):
    youtube_url = request.data.get("youtube_url")
    title = request.data.get("title") or "YouTube video"
    language = request.data.get("language") or "en"

    if not youtube_url:
        return Response(
            {"error": "youtube_url is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        raw_text = fetch_youtube_transcript(youtube_url, language=language)
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )

    content = ContentSource.objects.create(
        type=ContentSource.SourceType.YOUTUBE,
        title=title,
        raw_text=raw_text,
        language=language,
        status=ContentSource.Status.READY,
    )

    return Response(
        {"id": content.id, "title": content.title},
        status=status.HTTP_201_CREATED,
    )

logger = logging.getLogger(__name__)

@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def create_audio_content(request):
    # Debug – see what’s actually sent
    logger.info("FILES keys: %s", list(request.FILES.keys()))
    logger.info("DATA keys: %s", list(request.data.keys()))

    # Your frontend sends the file as "file"
    audio_file = (
        request.FILES.get("audio")
        or request.FILES.get("file")
        or request.FILES.get("audio_file")
        or (next(iter(request.FILES.values())) if request.FILES else None)
    )

    title = request.data.get("title") or (audio_file.name if audio_file else "Audio upload")
    language = request.data.get("language") or ""

    if not audio_file:
        return Response(
            {
                "success": False,
                "error": "No audio file provided. "
                         "Available FILES keys: " + str(list(request.FILES.keys()))
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # First create a ContentSource row in PROCESSING state and save the file
    content = ContentSource.objects.create(
        type=ContentSource.SourceType.AUDIO,   # ✅ field is "type"
        file=audio_file,                       # ✅ field is "file"
        language=language,
        title=title,
        status=ContentSource.Status.PROCESSING,
    )

    try:
        # 1) Transcribe with ElevenLabs (use saved file path)
        text = transcribe_audio_with_elevenlabs(content.file.path, language=language)

        # 2) Clean + chunk
        cleaned = clean_text(text)
        chunks = simple_chunk_text(cleaned)

        # 3) Save chunks with correct FK + field names
        ContentChunk.objects.bulk_create([
            ContentChunk(
                content=content,    # ✅ FK name is "content"
                index=i,            # ✅ field name is "index"
                text=chunk,
            )
            for i, chunk in enumerate(chunks)
        ])

        # 4) Update ContentSource now that processing succeeded
        content.raw_text = cleaned
        content.status = ContentSource.Status.READY
        content.error_message = ""
        content.save()

        return Response(
            {
                "success": True,
                "id": content.id,
                "title":content.title,
                "chunk_count": len(chunks),
            },
            status=status.HTTP_201_CREATED,
        )

    except Exception as e:
        logger.exception("Error while processing audio upload")
        content.status = ContentSource.Status.FAILED
        content.error_message = str(e)
        content.save()

        return Response(
            {
                "success": False,
                "error": "Failed to transcribe audio.",
                "details": str(e),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def create_document_content(request):
    serializer = DocumentContentCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    file = serializer.validated_data["file"]
    language = serializer.validated_data.get("language", "")
    title = serializer.validated_data.get("title") or file.name
    description = serializer.validated_data.get("description", "")

    allowed_doc_exts = (".pdf", ".png", ".jpg", ".jpeg")
    filename = file.name.lower()
    if not filename.endswith(allowed_doc_exts):
        return Response(
            {"detail": "Unsupported document format. Use PDF or image (PNG/JPG)."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    content = ContentSource.objects.create(
        type=ContentSource.SourceType.DOCUMENT,
        file=file,
        language=language,
        title=title,
        description=description,
        status=ContentSource.Status.PROCESSING,
    )

    try:
        path = content.file.path
        language_code = (language or "en").lower()

        tesseract_lang = "eng"
        if language_code.startswith("en"):
            tesseract_lang = "eng"
        elif language_code.startswith("az"):
            tesseract_lang = "aze"

        poppler_path = None

        if filename.endswith(".pdf"):
            extracted_text = extract_text_from_pdf(
                pdf_path=path,
                language=tesseract_lang,
                poppler_path=None,
            )
        else:
            extracted_text = extract_text_from_image_file(
                image_path=path,
                language=tesseract_lang,
            )

        if not extracted_text:
            raise RuntimeError("OCR extraction returned empty text.")

        extracted_text = clean_text(extracted_text)
        content.raw_text = extracted_text
        content.save()

        chunks = simple_chunk_text(extracted_text, max_chars=1000)
        for idx, chunk_text in enumerate(chunks, start=1):
            ContentChunk.objects.create(
                content=content,
                index=idx,
                text=chunk_text,
                tokens_estimate=len(chunk_text.split()),
            )

        content.status = ContentSource.Status.READY
        content.save()

    except Exception as e:
        content.status = ContentSource.Status.FAILED
        content.error_message = str(e)
        content.save()
        return Response(
            {"detail": "Failed to process document content", "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    output_serializer = ContentSourceSerializer(content, context={"request": request})
    return Response(output_serializer.data, status=status.HTTP_201_CREATED)
