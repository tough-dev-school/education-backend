from django.urls import include, path
from rest_framework.routers import SimpleRouter

from apps.homework.api.views import AnswerViewSet, AttachmentUploadView, CrossCheckView, ImageUploadView, QuestionView, ReactionViewSet

router = SimpleRouter()
router.register("answers", AnswerViewSet)

reaction_router = SimpleRouter()
reaction_router.register("reactions", ReactionViewSet)

urlpatterns = [
    path("questions/<uuid:slug>/", QuestionView.as_view()),
    path("crosschecks/", CrossCheckView.as_view()),
    path("answers/image/", ImageUploadView.as_view()),
    path("answers/<uuid:answer_slug>/attachment/", AttachmentUploadView.as_view()),
    path("", include(router.urls)),
    path("answers/<uuid:answer_slug>/", include(reaction_router.urls)),
]
