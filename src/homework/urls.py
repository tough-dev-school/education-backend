from django.urls import include, path
from rest_framework.routers import SimpleRouter

from homework.api.views import AnswerCommentView, QuestionView
from homework.api.viewsets import AnswerViewSet

router = SimpleRouter()
router.register('answers', AnswerViewSet)

urlpatterns = [
    path('questions/<uuid:slug>/', QuestionView.as_view()),
    path('comments/', AnswerCommentView.as_view()),
    path('', include(router.urls)),
]
