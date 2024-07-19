from django.urls import include, path
from rest_framework.routers import SimpleRouter

from apps.homework.api import views
from apps.homework.api.viewsets import AnswerViewSet, ReactionViewSet

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
