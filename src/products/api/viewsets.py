from rest_framework.mixins import RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from app.permissions import AllowAny
from orders.api.base import PromocodeView
from orders.api.base import PurchaseView
from products.api import serializers
from products.models import Course


class CourseViewSet(GenericViewSet, RetrieveModelMixin):
    lookup_field = "slug"
    serializer_class = serializers.CourseSerializer
    queryset = Course.objects.all()
    permission_classes = [AllowAny]


class CoursePromocodeView(PromocodeView):
    product_model = Course


class CoursePurchaseView(PurchaseView):
    product_model = Course
