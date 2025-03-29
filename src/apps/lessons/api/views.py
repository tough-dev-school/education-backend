from typing import TYPE_CHECKING

from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from apps.lessons.api.filters import LessonFilterSet
from apps.lessons.api.serializers import LessonForUserSerializer
from apps.lessons.models import Lesson
from core.api.mixins import DisablePaginationWithQueryParamMixin

if TYPE_CHECKING:
    from apps.lessons.models.lesson import LessonQuerySet


class LessonListView(DisablePaginationWithQueryParamMixin, ListAPIView):
    """List lessons, accessible to user. Better use it filtering by course"""

    serializer_class = LessonForUserSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = LessonFilterSet

    def get_queryset(self) -> "LessonQuerySet":
        return Lesson.objects.for_viewset(self.request.user)
