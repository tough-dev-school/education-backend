from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect
from rest_framework.decorators import action

from app.viewsets import ReadOnlyAppViewSet
from orders.api.validators import PurchaseValidator
from orders.creator import OrderCreator
from tinkoff.client import TinkoffBank
from users.creator import UserCreator


class PurchaseViewSet(ReadOnlyAppViewSet):
    """Abstract viewset for purchasable items"""
    validator_class = PurchaseValidator

    def get_validator_class(self):
        if self.validator_class is None:
            raise ImproperlyConfigured('Please set validator_class class variable')

        return self.validator_class

    @action(methods=['POST'], detail=True)
    def purchase(self, request, pk=None, **kwargs):
        data = request.POST

        self._validate(data)

        order = self._create_order(data=data)
        payment_link = self.get_payment_link(order, success_url=data.get('success_url'))

        return HttpResponseRedirect(redirect_to=payment_link)

    def _validate(self, data):
        Validator = self.get_validator_class()
        Validator.do(data)

    def _create_order(self, data):
        return OrderCreator(
            user=UserCreator(
                name=data['name'],
                email=data['email'],
                subscribe=data.get('subscribe', False),
            )(),
            item=self.get_object(),
            price=data['price'],
        )()

    def get_payment_link(self, order, success_url=None):
        bank = TinkoffBank(order=order, success_url=success_url)

        return bank.get_initial_payment_url()
