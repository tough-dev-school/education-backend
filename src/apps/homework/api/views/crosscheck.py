from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from apps.homework.api.serializers import CrossCheckSerializer
from apps.homework.models import AnswerCrossCheck, Question
from core.helpers import is_valid_uuid


@extend_schema(
    parameters=[
        OpenApiParameter(name="question", type=OpenApiTypes.UUID, required=True, description="Question id"),
    ],
)
class CrossCheckView(generics.ListAPIView):
    """Crosscheck status by question"""

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
