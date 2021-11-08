from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt import views as jwt

from a12n.api.throttling import AuthAnonRateThrottle
from a12n.models import PasswordlessAuthToken
from a12n.utils import get_jwt
from app.permissions import SuperUserOnly
from app.tasks import send_mail
from app.views import AnonymousAPIView
from users.models import User


class IEmailJSONWebTokenSerializer(jwt.JSONWebTokenSerializer):

    def validate(self, data):
        """Lower username, if it is an email.
        Enables case-insensitive email login
        """
        username = data.get(self.username_field)
        try:
            validate_email(username)
        except ValidationError:
            pass
        else:
            data[self.username_field] = username.lower()
        return super().validate(data)


class CustomObtainJSONWebTokenView(jwt.BaseJSONWebTokenAPIView):
    serializer_class = IEmailJSONWebTokenSerializer


class ObtainJSONWebTokenView(CustomObtainJSONWebTokenView):
    throttle_classes = [AuthAnonRateThrottle]


class RefreshJSONWebTokenView(jwt.RefreshJSONWebTokenView):
    throttle_classes = [AuthAnonRateThrottle]


class RequestPasswordLessToken(AnonymousAPIView):
    throttle_classes = [AuthAnonRateThrottle]

    def get(self, request, user_email: str):
        user = User.objects.filter(email=user_email).first()
        if user is not None:
            token = PasswordlessAuthToken.objects.create(user=user)
            send_mail.delay(
                to=user.email,
                template_id='passwordless-token',
                ctx=dict(
                    name=str(user),
                    action_url=token.get_absolute_url(),
                ),
                disable_antispam=True,
            )

        return Response({'ok': True})


class ObtainJSONWebTokenViaPasswordlessToken(AnonymousAPIView):
    throttle_classes = [AuthAnonRateThrottle]

    def get(self, request, token):
        token = get_object_or_404(PasswordlessAuthToken.objects.valid(), token=token)

        token.mark_as_used()

        return Response({
            'token': get_jwt(token.user),
        })


class ObtainJSONWebTokenViaUserId(APIView):
    permission_classes = [SuperUserOnly]

    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)

        return Response({
            'token': get_jwt(user),
        })
