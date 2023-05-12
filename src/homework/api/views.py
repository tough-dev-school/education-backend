from rest_framework import generics
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated

from django.db.models import QuerySet

from homework.api import serializers
from homework.api.filtersets import AnswerCommentFilterSet
from homework.api.permissions import ShouldHavePurchasedCoursePermission
from homework.models import Answer
from homework.models import AnswerImage
from homework.models import Question


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
    parser_classes = [MultiPartParser]
    serializer_class = serializers.AnswerImageSerializer
    queryset = AnswerImage.objects.all()
