from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from app.current_user import get_current_user
from users.api.serializers import UserSerializer
from users.models import User
from users.services import UserUpdater


class SelfView(GenericAPIView):
    serializer_class = UserSerializer

    def get(self, *args):
        user = self.get_object()
        serializer = self.get_serializer(user)

        return Response(serializer.data)

    def patch(self, request):

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
        return self.get_queryset().get(pk=user.pk)

    def get_queryset(self):
        return User.objects.filter(is_active=True)
