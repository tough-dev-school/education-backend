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
        validators.PurchaseValidator.do(request.POST)

        OrderCreator(
            user=UserCreator(
                name=request.POST['name'],
                email=request.POST['email'],
            )(),
            item=self.get_object(),
            price=request.POST['price'],
        )()

        return Response(status=201)


class CourseViewSet(ReadOnlyAppViewSet):
    lookup_field = 'slug'
    serializer_class = serializers.CourseSerializer
    queryset = Course.objects.all()
    permission_classes = [AllowAny]
