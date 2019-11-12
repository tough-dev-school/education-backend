from django.http import HttpResponseRedirect
from rest_framework.decorators import action

from app.permissions import AllowAny
from app.viewsets import ReadOnlyAppViewSet
from courses.api import serializers, validators
from courses.models import Course, Record
from orders.creator import OrderCreator
from tinkoff.client import TinkoffBank
from users.creator import UserCreator


class RecordViewSet(ReadOnlyAppViewSet):
    lookup_field = 'slug'
    serializer_class = serializers.RecordSerializer
    queryset = Record.objects.all()
    permission_classes = [AllowAny]

    @action(methods=['POST'], detail=True)
    def purchase(self, request, pk=None, **kwargs):
        validators.PurchaseValidator.do(request.POST)

        order = self._create_order(data=request.POST)
        payment_link = self.get_payment_link(order, success_url=request.POST.get('success_url'))

        return HttpResponseRedirect(redirect_to=payment_link)

    def _create_order(self, data):
        return OrderCreator(
            user=UserCreator(
                name=data['name'],
                email=data['email'],
            )(),
            item=self.get_object(),
            price=data['price'],
        )()

    def get_payment_link(self, order, success_url=None):
        bank = TinkoffBank(order=order, success_url=success_url)

        return bank.get_initial_payment_url()


class CourseViewSet(ReadOnlyAppViewSet):
    lookup_field = 'slug'
    serializer_class = serializers.CourseSerializer
    queryset = Course.objects.all()
    permission_classes = [AllowAny]
