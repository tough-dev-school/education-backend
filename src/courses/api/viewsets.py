from app.permissions import AllowAny
from app.viewsets import ReadOnlyAppViewSet
from courses.api import serializers
from courses.models import Course, Record


class RecordViewSet(ReadOnlyAppViewSet):
    lookup_field = 'slug'
    serializer_class = serializers.RecordSerializer
    queryset = Record.objects.all()
    permission_classes = [AllowAny]


class CourseViewSet(ReadOnlyAppViewSet):
    lookup_field = 'slug'
    serializer_class = serializers.CourseSerializer
    queryset = Course.objects.all()
    permission_classes = [AllowAny]
