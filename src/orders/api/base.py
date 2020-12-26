from typing import Optional

from django.http import HttpResponseRedirect
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from app.pricing import format_price
from app.viewsets import ReadOnlyAppViewSet
from orders.api.validators import GiftValidator, PurchaseValidator
from orders.models import Order, PromoCode
from orders.services.order_creator import OrderCreator
from tinkoff.client import TinkoffBank
from users.creator import UserCreator
from users.models import User


class PurchaseViewSet(ReadOnlyAppViewSet):
    """Abstract viewset for purchasable items"""
    @action(methods=['POST'], detail=True)
    def purchase(self, request, pk=None, **kwargs):
        """Direct order purchase"""
        data = request.POST

        PurchaseValidator.do(data)

        order = self._create_order(data=data)
        payment_link = self.get_payment_link(order, success_url=data.get('success_url'))

        return HttpResponseRedirect(redirect_to=payment_link)

    @action(methods=['POST'], detail=True)
    def gift(self, request, pk=None, **kwargs):
        """Purchase as a gift"""
        data = request.POST

        GiftValidator.do(data)

        order = self._create_gift(data=data)
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

    def _create_order(self, data) -> Order:
        return OrderCreator(
            user=self._create_user(data['name'], data['email'], subscribe=data.get('subscribe', False)),
            item=self.get_object(),
            promocode=data.get('promocode', None),
        )()

    def _create_gift(self, data) -> Order:
        do_subscribe = data.get('subscribe', False)

        return OrderCreator(
            user=self._create_user(data['receiver_name'], data['receiver_email'], subscribe=do_subscribe),
            giver=self._create_user(data['giver_name'], data['giver_email'], subscribe=do_subscribe),
            item=self.get_object(),
            desired_shipment_date=data['desired_shipment_date'],
            gift_message=data.get('gift_message', ''),
            promocode=data.get('promocode', None),
        )()

    def _create_user(self, name: str, email: str, subscribe: bool = False) -> User:
        return UserCreator(
            name=name,
            email=email,
            subscribe=subscribe,
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
