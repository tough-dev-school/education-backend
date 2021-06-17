from django.urls import include, path
from rest_framework.routers import SimpleRouter

from products.api.viewsets import BundleViewSet, CourseViewSet, RecordViewSet

product_router = SimpleRouter()
product_router.register('courses', CourseViewSet)
product_router.register('records', RecordViewSet)
product_router.register('bundles', BundleViewSet)

urlpatterns = [
    path('', include(product_router.urls)),
]
