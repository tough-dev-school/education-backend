from rest_framework.routers import SimpleRouter

from django.urls import include
from django.urls import path

from products.api.viewsets import BundleViewSet
from products.api.viewsets import CourseViewSet
from products.api.viewsets import RecordViewSet

product_router = SimpleRouter()
product_router.register("courses", CourseViewSet)
product_router.register("records", RecordViewSet)
product_router.register("bundles", BundleViewSet)

urlpatterns = [
    path("", include(product_router.urls)),
]
