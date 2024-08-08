from django.urls import path

from apps.stripebank.api.views import StripeWebhookKZTView, StripeWebhookUSDView
from apps.tinkoff.api.views import DolyameNotificationsView, TinkoffPaymentNotificationsView

urlpatterns = [
    path("tinkoff-notifications/", TinkoffPaymentNotificationsView.as_view()),
    path("dolyame-notifications/", DolyameNotificationsView.as_view()),
    path("stripe-webhooks/", StripeWebhookUSDView.as_view()),
    path("stripe-webhooks/kz/", StripeWebhookKZTView.as_view()),
]
