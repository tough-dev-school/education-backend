from django.utils.decorators import method_decorator
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated

from apps.lms.api.filters import LessonFilterSet, ModuleFilterSet
from apps.lms.api.serializers import LessonSerializer, ModuleDetailSerializer
from apps.lms.models import Lesson, Module
from apps.lms.models.lesson import LessonQuerySet
from apps.lms.models.module import ModuleQuerySet
from core.api.mixins import DisablePaginationWithQueryParamMixin
from core.viewsets import ReadOnlyAppViewSet


@method_decorator(
    extend_schema(
        description="Get a lesson by id",
    ),
    name="retrieve",
)
class LessonViewSet(DisablePaginationWithQueryParamMixin, ReadOnlyAppViewSet):
    """List lessons, accessible to user. Better use it filtering by module"""

    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = LessonFilterSet
    queryset = Lesson.objects.for_viewset()

    def get_queryset(self) -> LessonQuerySet:
        queryset: LessonQuerySet = super().get_queryset()  # type: ignore

        if self.request.user.has_perm("studying.purchased_all_courses"):
            return queryset

        return queryset.for_user(self.request.user).exclude_not_opened()  # type: ignore


@method_decorator(
    extend_schema(
        description="Get a module by id",
    ),
    name="retrieve",
)
class ModuleViewSet(DisablePaginationWithQueryParamMixin, ReadOnlyAppViewSet):
    """List modules, accessible to user. Better use it filtering by course"""

    serializer_class = ModuleDetailSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = ModuleFilterSet
    queryset = Module.objects.for_viewset()

    def get_queryset(self) -> ModuleQuerySet:
        queryset: ModuleQuerySet = super().get_queryset()  # type: ignore

        if self.request.user.has_perm("studying.purchased_all_courses"):
            if self.action == "retrieve":
                return queryset
            return queryset

        return queryset.for_user(self.request.user)  # type: ignore
