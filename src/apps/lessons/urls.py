from django.urls import path

from apps.lessons.api.views import LessonListView

urlpatterns = [
    path("", LessonListView.as_view()),
]
