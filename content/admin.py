from django.contrib import admin
from .models import ContentSource, ContentChunk

@admin.register(ContentSource)
class ContentSourceAdmin(admin.ModelAdmin):
    list_display = ("id", "type", "title", "status", "created_at")
    list_filter = ("type", "status")
    search_fields = ("title", "youtube_url")

@admin.register(ContentChunk)
class ContentChunkAdmin(admin.ModelAdmin):
    list_display = ("id", "content", "index", "tokens_estimate")
    list_filter = ("content",)