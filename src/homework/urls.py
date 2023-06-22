from rest_framework.routers import SimpleRouter

from django.urls import include
from django.urls import path

from homework.api import views
from homework.api.viewsets import AnswerViewSet
from homework.api.viewsets import ReactionViewSet

router = SimpleRouter()
router.register("answers", AnswerViewSet)

reaction_router = SimpleRouter()
reaction_router.register("reactions", ReactionViewSet)

urlpatterns = [
    path("questions/<uuid:slug>/", views.QuestionView.as_view()),
    path("comments/", views.AnswerCommentView.as_view()),
    path("answers/image/", views.AnswerImageUploadView.as_view()),
    path("", include(router.urls)),
    path("answers/<uuid:answer_slug>/", include(reaction_router.urls)),
]
