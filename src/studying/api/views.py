from django.db.models import QuerySet
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from app.views import AuthenticatedRequest
from products.models import Course
from studying.api.serializers import CourseSerializer
from studying.models import Study


class PurchasedCoursesView(ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    request: AuthenticatedRequest

    def get_queryset(self) -> QuerySet[Course]:
        studies = Study.objects.filter(student=self.request.user)

        return Course.objects.for_lms().filter(id__in=studies.values('course'))
