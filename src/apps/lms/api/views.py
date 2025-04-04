from typing import TYPE_CHECKING

from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from apps.lms.api.filters import LessonFilterSet, ModuleFilterSet
from apps.lms.api.serializers import LessonForUserSerializer, ModuleSerializer
from apps.lms.models import Lesson, Module
from core.api.mixins import DisablePaginationWithQueryParamMixin

if TYPE_CHECKING:
    from apps.lms.models.lesson import LessonQuerySet
    from apps.lms.models.module import ModuleQuerySet


class LessonListView(DisablePaginationWithQueryParamMixin, ListAPIView):
    """List lessons, accessible to user. Better use it filtering by module"""

    serializer_class = LessonForUserSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = LessonFilterSet

    def get_queryset(self) -> "LessonQuerySet":
        return Lesson.objects.for_viewset(self.request.user)


class ModuleListView(DisablePaginationWithQueryParamMixin, ListAPIView):
    """List modules, accessible to user. Better use it filtering by course"""

    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = ModuleFilterSet

    def get_queryset(self) -> "ModuleQuerySet":
        return Module.objects.for_viewset(self.request.user)
