from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from users.api.serializers import UserSerializer, UserUpdateSerializer
from users.models import User


class SelfView(GenericAPIView):
    serializer_class = UserSerializer

    def get(self, *args):
        user = self.get_object()
        serializer = self.get_serializer(user)

        return Response(serializer.data)

    def patch(self, request):
        user = self.get_object()

        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user.refresh_from_db()
        return Response(
            self.get_serializer(user).data,
        )

    def get_object(self) -> User:
        return self.get_queryset().get(pk=self.request.user.pk)

    def get_queryset(self):
        return User.objects.filter(is_active=True)
