from rest_framework.generics import RetrieveAPIView

from users.api.serializers import UserSerializer
from users.models import User


class UserView(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
