from rest_framework.routers import SimpleRouter

from django.urls import include
from django.urls import path

from products.api.viewsets import CoursePromocodeView
from products.api.viewsets import CoursePurchaseView
from products.api.viewsets import CourseViewSet

product_router = SimpleRouter()
product_router.register("courses", CourseViewSet)

urlpatterns = [
    path("", include(product_router.urls)),
    path("courses/<str:slug>/promocode/", CoursePromocodeView.as_view()),
    path("courses/<str:slug>/purchase/", CoursePurchaseView.as_view()),
]
