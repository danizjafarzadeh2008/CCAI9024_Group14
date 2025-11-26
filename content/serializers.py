from rest_framework import serializers
from .models import ContentSource, ContentChunk

class ContentChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentChunk
        fields = ["id", "index", "text", "tokens_estimate"]


class ContentSourceSerializer(serializers.ModelSerializer):
    chunks = ContentChunkSerializer(many=True, read_only=True)

    class Meta:
        model = ContentSource
        fields = [
            "id",
            "type",
            "title",
            "description",
            "youtube_url",
            "file",
            "language",
            "raw_text",
            "status",
            "error_message",
            "created_at",
            "chunks",
        ]
        read_only_fields = [
            "raw_text",
            "status",
            "error_message",
            "created_at",
            "chunks",
        ]


class YouTubeContentCreateSerializer(serializers.Serializer):
    youtube_url = serializers.URLField()
    language = serializers.CharField(required=False, allow_blank=True, default="")
    title = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)


class AudioContentCreateSerializer(serializers.Serializer):
    file = serializers.FileField()
    language = serializers.CharField(required=False, allow_blank=True, default="")
    title = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)


class DocumentContentCreateSerializer(serializers.Serializer):
    file = serializers.FileField()
    language = serializers.CharField(required=False, allow_blank=True, default="")
    title = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
