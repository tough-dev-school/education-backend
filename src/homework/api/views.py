from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from homework.api.filtersets import AnswerCommentFilterSet
from homework.api.permissions import ShouldHavePurchasedCoursePermission
from homework.api.serializers import AnswerCommentTreeSerializer, QuestionSerializer
from homework.models import Answer, Question
from homework.models.answer import AnswerQuerySet


class QuestionView(RetrieveAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [ShouldHavePurchasedCoursePermission]
    lookup_field = 'slug'


class AnswerCommentView(ListAPIView):
    queryset = Answer.objects.for_viewset()
    serializer_class = AnswerCommentTreeSerializer
    filterset_class = AnswerCommentFilterSet
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self) -> AnswerQuerySet:
        return super().get_queryset().root_only().for_user(self.request.user)  # type: ignore
