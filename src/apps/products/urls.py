from django.urls import path

from apps.products.api.views import PromocodeView, PurchaseView

urlpatterns = [
    path("courses/<str:slug>/promocode/", PromocodeView.as_view()),
    path("courses/<str:slug>/purchase/", PurchaseView.as_view()),
]
