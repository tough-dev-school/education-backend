from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from apps.homework.api import serializers
from apps.homework.api.filtersets import AnswerCommentFilterSet
from apps.homework.api.serializers import CrossCheckSerializer
from apps.homework.models import Answer, AnswerCrossCheck, AnswerImage, Question
from core.helpers import is_valid_uuid


class QuestionView(generics.RetrieveAPIView):
    queryset = Question.objects.all()
    serializer_class = serializers.QuestionDetailSerializer
    lookup_field = "slug"

    def get_queryset(self) -> QuerySet[Question]:
        queryset = super().get_queryset()

        return queryset.for_user(self.request.user)  # type: ignore


class AnswerCommentView(generics.ListAPIView):
    """Recursively list answer comments"""

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


class ImageUploadView(generics.CreateAPIView):
    """Upload an image"""

    permission_classes = [IsAuthenticated]
    serializer_class = serializers.AnswerImageSerializer
    queryset = AnswerImage.objects.all()


class CrossCheckView(generics.ListAPIView):
    """Crosscheck status"""

    queryset = AnswerCrossCheck.objects.for_viewset()
    serializer_class = CrossCheckSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self) -> QuerySet[AnswerCrossCheck]:
        return super().get_queryset().filter(checker=self.request.user)

    def filter_queryset(self, queryset: QuerySet[AnswerCrossCheck]) -> QuerySet[AnswerCrossCheck]:
        question_slug = self.request.GET.get("question")

        if question_slug is None or not is_valid_uuid(question_slug):
            raise ValidationError("Please add 'question' GET param")

        questions = Question.objects.neighbours(
            of_question=get_object_or_404(Question, slug=question_slug),
        )

        return queryset.filter(answer__question__in=questions.values_list("pk"))
