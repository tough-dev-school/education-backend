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
    queryset = Lesson.objects.none()  # needed for swaggeer

    def get_queryset(self) -> "LessonQuerySet":
        queryset = Lesson.objects.for_viewset()

        if self.request.user.has_perm("studying.purchased_all_courses"):
            # Adding fake data for the serializers
            return queryset.with_fake_is_sent().with_fake_crosscheck_stats()

        return (
            queryset.for_user(
                self.request.user,  # type: ignore
            )
            .with_is_sent(
                self.request.user,  # type: ignore
            )
            .with_crosscheck_stats(
                self.request.user,  # type: ignore
            )
        )


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
