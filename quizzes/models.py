from django.db import models
from content.models import ContentSource

class Quiz(models.Model):
    title = models.CharField(max_length=255)
    contents = models.ManyToManyField(ContentSource, related_name="quizzes")

    settings = models.JSONField()
    custom_instructions = models.TextField(blank=True)

    output_json = models.JSONField(blank=True, null=True)

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
        return self.title


class Question(models.Model):
    class QuestionType(models.TextChoices):
        MCQ = "MCQ", "Multiple Choice"
        FRQ = "FRQ", "Free Response"
        TRUE_FALSE = "TRUE_FALSE", "True/False"
        CLOZE = "CLOZE", "Cloze"
        MATCHING = "MATCHING", "Matching"
        REASONING = "REASONING", "Reasoning"

    quiz = models.ForeignKey(Quiz, related_name="questions", on_delete=models.CASCADE)
    index = models.PositiveIntegerField()
    type = models.CharField(max_length=20, choices=QuestionType.choices)

    prompt = models.TextField()
    bloom_level = models.CharField(max_length=50, blank=True)
    difficulty = models.CharField(max_length=20, blank=True)
    explanation = models.TextField(blank=True)


    correct_answer = models.TextField(blank=True)

    metadata = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ["quiz", "index"]

    def __str__(self):
        return f"Q{self.index} ({self.type}) of {self.quiz_id}"


class Choice(models.Model):
    question = models.ForeignKey(Question, related_name="choices", on_delete=models.CASCADE)
    label = models.CharField(max_length=5)
    text = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.question_id} - {self.label}"
