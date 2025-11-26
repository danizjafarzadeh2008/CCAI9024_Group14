from django.db import models

class ContentSource(models.Model):
    class SourceType(models.TextChoices):
        YOUTUBE = "YOUTUBE", "YouTube"
        AUDIO = "AUDIO", "Audio"
        DOCUMENT = "DOCUMENT", "Document"

    type = models.CharField(max_length=20, choices=SourceType.choices)
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    youtube_url = models.URLField(blank=True, null=True)
    file = models.FileField(upload_to="uploads/", blank=True, null=True)

    language = models.CharField(max_length=10, blank=True)

    raw_text = models.TextField(blank=True)

    class Status(models.TextChoices):
        PROCESSING = "PROCESSING", "Processing"
        READY = "READY", "Ready"
        FAILED = "FAILED", "Failed"

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PROCESSING,
    )
    error_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        base = self.title or self.youtube_url or (self.file.name if self.file else "Content")
        return f"{self.type} - {base}"


class ContentChunk(models.Model):
    content = models.ForeignKey(
        ContentSource,
        related_name="chunks",
        on_delete=models.CASCADE,
    )
    index = models.PositiveIntegerField()
    text = models.TextField()
    tokens_estimate = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["content", "index"]
        unique_together = ("content", "index")

    def __str__(self):
        return f"Chunk {self.index} of {self.content_id}"
