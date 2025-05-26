from django.db.models import QuerySet
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.homework.api import serializers
from apps.homework.api.filtersets import AnswerCommentFilterSet, AnswerCrossCheckFilterSet
from apps.homework.api.permissions import ShouldHavePurchasedCoursePermission
from apps.homework.api.serializers import AnswerCrossCheckSerializer
from apps.homework.models import Answer, AnswerCrossCheck, AnswerImage, Question


class QuestionView(generics.RetrieveAPIView):
    queryset = Question.objects.all()
    serializer_class = serializers.QuestionDetailSerializer
    permission_classes = [ShouldHavePurchasedCoursePermission]
    lookup_field = "slug"


class AnswerCommentView(generics.ListAPIView):
    """Recursive list list answer comments"""

    queryset = Answer.objects.for_viewset()
    serializer_class = serializers.AnswerCommentTreeSerializer
    filterset_class = AnswerCommentFilterSet
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self) -> QuerySet[Answer]:
        queryset = super().get_queryset().root_only()  # type: ignore

        if self.request.user.has_perm("homework.see_all_answers"):
            return queryset

        return queryset.for_user(self.request.user)


class AnswerImageUploadView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.AnswerImageSerializer
    queryset = AnswerImage.objects.all()


class AnswerCrossCheckView(generics.ListAPIView):
    """Retrieves crosscheck status"""

    queryset = AnswerCrossCheck.objects.for_viewset()
    serializer_class = AnswerCrossCheckSerializer
    filterset_class = AnswerCrossCheckFilterSet
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self) -> QuerySet[AnswerCrossCheck]:
        return super().get_queryset().filter(checker=self.request.user)
