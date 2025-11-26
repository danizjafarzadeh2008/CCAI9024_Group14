from django.urls import path
from . import views

urlpatterns = [
    path("ping/", views.ping, name="content-ping"),
    path("list/", views.list_content, name="content-list"),
    path("youtube/", views.create_youtube_content, name="content-youtube-create"),
    path("audio/", views.create_audio_content, name="content-audio-create"),
    path("document/", views.create_document_content, name="content-document-create"),
]
