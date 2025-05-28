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
    queryset = Lesson.objects.for_viewset()

    def get_queryset(self) -> "LessonQuerySet":
        queryset = super().get_queryset()

        if not self.request.user.has_perm("studying.purchased_all_courses"):
            return queryset.with_annotations(self.request.user).for_user(self.request.user)  # type: ignore
        else:
            # Adding fake data for the serializers if user may access all courses
            return queryset.with_fake_annotations()  # type: ignore


class ModuleListView(DisablePaginationWithQueryParamMixin, ListAPIView):
    """List modules, accessible to user. Better use it filtering by course"""

    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = ModuleFilterSet
    queryset = Module.objects.none()  # needed for swagger

    def get_queryset(self) -> "ModuleQuerySet":
        queryset = Module.objects.for_viewset()

        if self.request.user.has_perm("studying.purchased_all_courses"):
            return queryset

        return queryset.for_user(self.request.user)  # type: ignore
