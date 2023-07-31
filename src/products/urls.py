from django.urls import path

from products.api.views import PromocodeView
from products.api.views import PurchaseView

urlpatterns = [
    path("courses/<str:slug>/promocode/", PromocodeView.as_view()),
    path("courses/<str:slug>/purchase/", PurchaseView.as_view()),
]
