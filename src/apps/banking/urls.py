from django.urls import path

from apps.stripebank.api.views import StripeWebhookView
from apps.tinkoff.api.views import DolyameNotificationsView
from apps.tinkoff.api.views import TinkoffPaymentNotificationsView

urlpatterns = [
    path("tinkoff-notifications/", TinkoffPaymentNotificationsView.as_view()),
    path("dolyame-notifications/", DolyameNotificationsView.as_view()),
    path("stripe-webhooks/", StripeWebhookView.as_view()),
]
