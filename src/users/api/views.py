from typing import Any

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions
from rest_framework.generics import GenericAPIView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response

from django.core.exceptions import ImproperlyConfigured

from app.current_user import get_current_user
from users.api.filters import UserFilter
from users.api.serializers import UserSerializer
from users.models import User
from users.services import UserUpdater


class SelfView(GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.for_view()

    def get(self, *args: Any) -> Response:
        user = self.get_object()
        serializer = self.get_serializer(user)

        return Response(serializer.data)

    def patch(self, request: Request) -> Response:
        user_updater = UserUpdater(
            user=self.get_object(),
            user_data=request.data,
        )

        user = user_updater()

        return Response(
            self.get_serializer(user).data,
        )

    def get_object(self) -> User:
        user = get_current_user()
        if user is not None:
            return self.get_queryset().get(pk=user.pk)

        raise ImproperlyConfigured("This code should not be ran")


class UserView(ListAPIView):
    filter_backends = (DjangoFilterBackend,)
    filterset_class = UserFilter
    pagination_class = None
    permission_classes = (IsAdminUser,)
    queryset = User.objects.for_view()
    serializer_class = UserSerializer
