from django.urls import path
from . import views

urlpatterns = [
    path("", views.create_quiz, name="quiz-create"),
    path("<int:pk>/", views.retrieve_quiz, name="quiz-detail"),
    path(
        "<int:quiz_id>/questions/<int:question_id>/regenerate/",
        views.regenerate_question,
        name="quiz-question-regenerate",
    ),
    path(
        "<int:quiz_id>/questions/<int:question_id>/explain/",
        views.explain_question,
        name="quiz-question-explain",
    ),
    path("<int:pk>/export/json/", views.export_quiz_json, name="quiz-export-json"),
    path("<int:pk>/export/csv/", views.export_quiz_csv, name="quiz-export-csv"),
]