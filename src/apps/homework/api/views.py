from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from django.db.models import QuerySet

from apps.homework.api import serializers
from apps.homework.api.filtersets import AnswerCommentFilterSet
from apps.homework.api.permissions import ShouldHavePurchasedCoursePermission
from apps.homework.models import Answer
from apps.homework.models import AnswerImage
from apps.homework.models import Question


class QuestionView(generics.RetrieveAPIView):
    queryset = Question.objects.all()
    serializer_class = serializers.QuestionSerializer
    permission_classes = [ShouldHavePurchasedCoursePermission]
    lookup_field = "slug"


class AnswerCommentView(generics.ListAPIView):
    queryset = Answer.objects.for_viewset()
    serializer_class = serializers.AnswerCommentTreeSerializer
    filterset_class = AnswerCommentFilterSet
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self) -> QuerySet[Answer]:
        return super().get_queryset().root_only().allowed_for_user(self.request.user)  # type: ignore


class AnswerImageUploadView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.AnswerImageSerializer
    queryset = AnswerImage.objects.all()
