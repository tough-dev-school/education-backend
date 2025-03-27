from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from apps.lessons.api.filters import LessonFilterSet
from apps.lessons.api.serializers import LessonSerializer
from apps.lessons.models import Lesson, LessonQuerySet
from core.api.mixins import DisablePaginationWithQueryParamMixin


class LessonListView(DisablePaginationWithQueryParamMixin, ListAPIView):
    """List all lessons for a specific course."""

    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = LessonFilterSet

    def get_queryset(self) -> LessonQuerySet:
        return Lesson.objects.for_user(self.request.user).for_viewset()
