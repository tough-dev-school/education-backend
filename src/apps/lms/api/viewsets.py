from django.utils.decorators import method_decorator
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated

from apps.lms.api.filters import LessonFilterSet
from apps.lms.api.serializers import LessonSerializer
from apps.lms.models import Lesson
from apps.lms.models.lesson import LessonQuerySet
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

        return queryset.for_user(self.request.user)  # type: ignore
