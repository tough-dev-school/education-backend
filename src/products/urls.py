from django.urls import path

from products.api.views import get_course_students
from products.api.views import PromocodeView
from products.api.views import PurchaseView

urlpatterns = [
    path("courses/<int:course_id>/students/", get_course_students),
    path("courses/<str:slug>/promocode/", PromocodeView.as_view()),
    path("courses/<str:slug>/purchase/", PurchaseView.as_view()),
]
