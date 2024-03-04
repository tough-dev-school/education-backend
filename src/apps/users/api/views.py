from typing import Any

from django.core.exceptions import ImproperlyConfigured
from django.db.models import QuerySet
from rest_framework import permissions
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from apps.users.api.serializers import UserSerializer
from apps.users.models import User
from apps.users.services import UserUpdater
from core.current_user import get_current_user


class SelfView(GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

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

    def get_queryset(self) -> QuerySet[User]:
        return User.objects.filter(is_active=True)
