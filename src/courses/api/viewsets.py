from rest_framework.decorators import action
from rest_framework.response import Response

from app.permissions import AllowAny
from app.viewsets import ReadOnlyAppViewSet
from courses.api import serializers, validators
from courses.models import Course, Record
from orders.creator import OrderCreator
from users.creator import UserCreator


class RecordViewSet(ReadOnlyAppViewSet):
    lookup_field = 'slug'
    serializer_class = serializers.RecordSerializer
    queryset = Record.objects.all()
    permission_classes = [AllowAny]

    @action(methods=['POST'], detail=True)
    def purchase(self, request, pk=None, **kwargs):
        validators.PurchaseValidator.do(request.data)

        OrderCreator(
            user=UserCreator(
                name=request.data['name'],
                email=request.data['email'],
            )(),
            item=self.get_object(),
            price=request.data['price'],
        )()

        return Response(status=201)


class CourseViewSet(ReadOnlyAppViewSet):
    lookup_field = 'slug'
    serializer_class = serializers.CourseSerializer
    queryset = Course.objects.all()
    permission_classes = [AllowAny]
