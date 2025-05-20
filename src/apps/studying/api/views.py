from django.db.models import QuerySet
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from apps.products.models import Course
from apps.studying.api.serializers import CourseSerializer
from core.api.mixins import DisablePaginationWithQueryParamMixin
from core.views import AuthenticatedRequest


class PurchasedCoursesView(DisablePaginationWithQueryParamMixin, ListAPIView):
    """List of courses, purchased by particular user"""

    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    request: AuthenticatedRequest

    def get_queryset(self) -> QuerySet[Course]:
        queryset = Course.objects.for_lms()
        if self.request.user.has_perm("studying.purchased_all_courses"):
            return queryset.all()

        return queryset.purchased_by(self.request.user)
