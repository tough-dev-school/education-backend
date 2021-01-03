
from app.permissions import AllowAny
from orders.api.base import PurchaseViewSet
from products.api import serializers
from products.models import Bundle, Course, Record


class RecordViewSet(PurchaseViewSet):
    lookup_field = 'slug'
    serializer_class = serializers.RecordSerializer
    queryset = Record.objects.all()
    permission_classes = [AllowAny]


class CourseViewSet(PurchaseViewSet):
    lookup_field = 'slug'
    serializer_class = serializers.CourseSerializer
    queryset = Course.objects.all()
    permission_classes = [AllowAny]


class BundleViewSet(PurchaseViewSet):
    lookup_field = 'slug'
    serializer_class = serializers.BundleSerializer
    queryset = Bundle.objects.all()
    permission_classes = [AllowAny]
