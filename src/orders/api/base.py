from typing import Optional

from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from app.pricing import format_price
from app.viewsets import ReadOnlyAppViewSet
from orders.api.validators import PurchaseValidator
from orders.creator import OrderCreator
from orders.models import PromoCode
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

    @action(methods=['GET'], detail=True)
    def promocode(self, request, pk=None, **kwargs):
        item = self.get_object()
        promocode = self._get_promocode(request)

        price = promocode.apply(item.price) if promocode is not None else item.price

        return Response({
            'price': price,
            'formatted_price': format_price(price),
        })

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
            promocode=data.get('promocode', None),
        )()

    def _get_promocode(self, request) -> Optional[PromoCode]:
        try:
            promocode_name = request.GET['promocode']
        except KeyError:
            raise ValidationError(detail='please use «promocode» request parameter')

        return PromoCode.objects.get_or_nothing(name=promocode_name)

    def get_payment_link(self, order, success_url=None):
        bank = TinkoffBank(order=order, success_url=success_url)

        return bank.get_initial_payment_url()
