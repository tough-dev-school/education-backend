from django.db.models import QuerySet
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from apps.products.models import Course
from apps.studying.api.serializers import CourseSerializer
from apps.studying.models import Study
from core.api.mixins import DisablePaginationWithQueryParamMixin
from core.views import AuthenticatedRequest


class PurchasedCoursesView(DisablePaginationWithQueryParamMixin, ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    request: AuthenticatedRequest

    def get_queryset(self) -> QuerySet[Course]:
        studies = Study.objects.filter(student=self.request.user)

        return Course.objects.for_lms().filter(id__in=studies.values("course"))
