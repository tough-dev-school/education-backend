from django.urls import path

from products.api.views import CoursePromocodeView
from products.api.views import CoursePurchaseView

urlpatterns = [
    path("courses/<str:slug>/promocode/", CoursePromocodeView.as_view()),
    path("courses/<str:slug>/purchase/", CoursePurchaseView.as_view()),
]
