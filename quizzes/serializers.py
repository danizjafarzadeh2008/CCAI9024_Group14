from rest_framework import serializers
from content.models import ContentSource
from .models import Quiz, Question, Choice


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ["id", "label", "text", "is_correct"]


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = [
            "id",
            "index",
            "type",
            "prompt",
            "bloom_level",
            "difficulty",
            "explanation",
            "correct_answer",
            "metadata",
            "choices",
        ]


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = [
            "id",
            "title",
            "settings",
            "custom_instructions",
            "output_json",
            "status",
            "error_message",
            "created_at",
            "questions",
        ]


class QuizCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    content_ids = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=False
    )
    settings = serializers.JSONField()
    custom_instructions = serializers.CharField(allow_blank=True, required=False)

    def validate_content_ids(self, value):
        if not value:
            raise serializers.ValidationError("At least one content_id is required.")
        return value

    def validate(self, attrs):
        settings = attrs.get("settings", {})
        if "num_questions" not in settings:
            raise serializers.ValidationError({"settings": "num_questions is required."})
        if "question_types" not in settings:
            raise serializers.ValidationError({"settings": "question_types is required."})
        return attrs
