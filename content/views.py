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


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def create_audio_content(request):
    serializer = AudioContentCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    file = serializer.validated_data["file"]
    language = serializer.validated_data.get("language", "")
    title = serializer.validated_data.get("title") or file.name
    description = serializer.validated_data.get("description", "")

    content = ContentSource.objects.create(
        type=ContentSource.SourceType.AUDIO,
        file=file,
        language=language,
        title=title,
        description=description,
        status=ContentSource.Status.PROCESSING,
    )

    allowed_extensions = (".mp3", ".wav", ".m4a", ".mp4")
    filename = file.name.lower()
    if not filename.endswith(allowed_extensions):
        content.status = ContentSource.Status.FAILED
        content.error_message = "Unsupported audio format"
        content.save()
        return Response(
            {
                "detail": "Unsupported audio format. Please upload MP3, WAV, M4A, or MP4."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        audio_path = content.file.path

        transcript_text = transcribe_audio_with_elevenlabs(
            file_path=audio_path,
            language=language or "",
        )

        if not transcript_text:
            raise RuntimeError("ElevenLabs transcription returned empty text.")

        transcript_text = clean_text(transcript_text)

        content.raw_text = transcript_text
        content.save()

        chunks = simple_chunk_text(transcript_text, max_chars=1000)
        for idx, chunk_text in enumerate(chunks, start=1):
            ContentChunk.objects.create(
                content=content,
                index=idx,
                text=chunk_text,
                tokens_estimate=len(chunk_text.split()),
            )

        content.status = ContentSource.Status.READY
        content.save()

    except RuntimeError as e:
        content.status = ContentSource.Status.FAILED
        content.error_message = str(e)
        content.save()
        return Response(
            {"detail": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        content.status = ContentSource.Status.FAILED
        content.error_message = str(e)
        content.save()
        return Response(
            {"detail": "Failed to process audio content", "error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    output_serializer = ContentSourceSerializer(content, context={"request": request})
    return Response(output_serializer.data, status=status.HTTP_201_CREATED)

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
