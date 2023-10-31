from django.core.management.base import BaseCommand

from apps.banking.atol.client import AtolClient
from apps.orders.models import Order


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        order = Order.objects.get(pk=1731)

        AtolClient(order=order)()
