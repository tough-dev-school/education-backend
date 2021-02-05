from django.conf import settings
from urllib.parse import urljoin

from app.banking import Bank


class TinkoffCredit(Bank):
    host = 'https://loans.tinkoff.ru/api/partners/'

    def get_initial_payment_url(self):
        pass

    def get_create_order_url(self):
        if settings.TINKOFF_CREDIT_DEMO_MODE:
            return urljoin(self.host, 'v1/lightweight/create-demo')

        return urljoin(self.host, 'v1/lightweight/create')

    @staticmethod
    def get_notification_url():
        return urljoin(settings.ABSOLUTE_HOST, '/api/v2/banking/tinkoff-credit-notifications/')
