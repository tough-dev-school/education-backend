from django.db.models import QuerySet
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.homework.api import serializers
from apps.homework.api.filtersets import AnswerCommentFilterSet, AnswerCrossCheckFilterSet
from apps.homework.api.permissions import ShouldHavePurchasedCoursePermission
from apps.homework.api.serializers import CrossCheckSerializer
from apps.homework.models import Answer, AnswerCrossCheck, AnswerImage, Question


class QuestionView(generics.RetrieveAPIView):
    queryset = Question.objects.all()
    serializer_class = serializers.QuestionDetailSerializer
    permission_classes = [ShouldHavePurchasedCoursePermission]
    lookup_field = "slug"

    def get_queryset(self) -> QuerySet[Question]:
        queryset = super().get_queryset()

        if self.request.user.is_anonymous:
            return queryset.none()

        if not self.request.user.has_perm("studying.purchased_all_courses"):
            return queryset.with_annotations(self.request.user)  # type: ignore
        else:
            # Adding fake data for the serializers if user may access all courses
            return queryset.with_fake_annotations()  # type: ignore


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
    filterset_class = AnswerCrossCheckFilterSet
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self) -> QuerySet[AnswerCrossCheck]:
        return super().get_queryset().filter(checker=self.request.user)
