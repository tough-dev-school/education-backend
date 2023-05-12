from rest_framework.routers import SimpleRouter

from django.urls import include
from django.urls import path

from homework.api import views
from homework.api.viewsets import AnswerViewSet

router = SimpleRouter()
router.register("answers", AnswerViewSet)

urlpatterns = [
    path("questions/<uuid:slug>/", views.QuestionView.as_view()),
    path("comments/", views.AnswerCommentView.as_view()),
    path("answers/image/", views.AnswerImageUploadView.as_view()),
    path("", include(router.urls)),
]
