from django.urls import path

from apps.orders.api import views

urlpatterns = [
    path("<str:slug>/confirm/", views.OrderConfirmationView.as_view(), name="confirm-order"),
]
