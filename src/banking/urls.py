from django.urls import path

from banking.api.views import AtolWebhookView
from stripebank.api.views import StripeWebhookView
from tinkoff.api.views import DolyameNotificationsView, TinkoffCreditNotificationsView, TinkoffPaymentNotificationsView

urlpatterns = [
    path('tinkoff-notifications/', TinkoffPaymentNotificationsView.as_view()),
    path('tinkoff-credit-notifications/', TinkoffCreditNotificationsView.as_view()),
    path('dolyame-notifications/', DolyameNotificationsView.as_view()),
    path('stripe-webhooks/', StripeWebhookView.as_view()),
    path('atol-webhooks/', AtolWebhookView.as_view()),
]
