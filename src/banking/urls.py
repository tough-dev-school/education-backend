from django.urls import path

from tinkoff.api.views import TinkoffCreditNotificationsView, TinkoffPaymentNotificationsView

urlpatterns = [
    path('tinkoff-notifications/', TinkoffPaymentNotificationsView.as_view()),
    path('tinkoff-credit-notifications/', TinkoffCreditNotificationsView.as_view()),
]
