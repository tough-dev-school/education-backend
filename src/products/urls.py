from rest_framework.routers import SimpleRouter

from django.urls import include
from django.urls import path

from products.api.viewsets import CourseViewSet

product_router = SimpleRouter()
product_router.register("courses", CourseViewSet)

urlpatterns = [
    path("", include(product_router.urls)),
]
