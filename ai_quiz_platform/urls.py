from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/content/", include("content.urls")),
    path("api/quizzes/", include("quizzes.urls")),
    path("", views.home, name="home"),
    path("upload/", views.upload_page, name="upload"),
    path("configure/", views.configure_page, name="configure"),
    path("quiz-loading/<int:quiz_id>/", views.quiz_loading_page, name="quiz-loading"),
    path("quiz/<int:quiz_id>/", views.quiz_detail_page, name="quiz-detail-page"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)