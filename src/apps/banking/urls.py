from django.conf import settings
from django.urls import path

from apps.banking.api.views import AtolWebhookView
from apps.stripebank.api.views import StripeWebhookView
from apps.tinkoff.api.views import DolyameNotificationsView
from apps.tinkoff.api.views import TinkoffCreditNotificationsView
from apps.tinkoff.api.views import TinkoffPaymentNotificationsView

urlpatterns = [
    path("tinkoff-notifications/", TinkoffPaymentNotificationsView.as_view()),
    path("tinkoff-credit-notifications/", TinkoffCreditNotificationsView.as_view()),
    path("dolyame-notifications/", DolyameNotificationsView.as_view()),
    path("stripe-webhooks/", StripeWebhookView.as_view()),
    path(f"atol-webhooks-{settings.ATOL_WEBHOOK_SALT}/", AtolWebhookView.as_view()),
]
