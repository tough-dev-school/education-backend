from django.urls import path

from apps.lms.api.views import LessonListView, ModuleListView

urlpatterns = [
    path("lessons/", LessonListView.as_view()),
    path("modules/", ModuleListView.as_view()),
]
