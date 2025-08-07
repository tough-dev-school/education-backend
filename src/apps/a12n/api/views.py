from dj_rest_auth import views as dj_rest_auth_views
from django.conf import settings
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt import views as jwt

from apps.a12n.api.serializers import OkSerializer, PasswordResetSerializer, TokenSerializer
from apps.a12n.api.throttling import AuthAnonRateThrottle
from apps.a12n.models import PasswordlessAuthToken
from apps.a12n.utils import get_jwt
from apps.mailing.tasks import send_mail
from apps.users.models import User
from core.permissions import SuperUserOnly
from core.views import AnonymousAPIView


class ObtainJSONWebTokenView(jwt.ObtainJSONWebTokenView):
    throttle_classes = [AuthAnonRateThrottle]


class RefreshJSONWebTokenView(jwt.RefreshJSONWebTokenView):
    throttle_classes = [AuthAnonRateThrottle]


@extend_schema(responses={200: OkSerializer})
class RequestPasswordLessToken(AnonymousAPIView):
    throttle_classes = [AuthAnonRateThrottle]

    def get(self, request: Request, user_email: str) -> Response:
        user = User.objects.filter(is_active=True).filter(email=user_email).first()
        if user is not None:
            passwordless_auth_token = PasswordlessAuthToken.objects.create(user=user)
            send_mail.delay(
                to=user.email,
                template_id=settings.PASSWORDLESS_TOKEN_TEMPLATE_ID,
                ctx={
                    "name": str(user),
                    "action_url": passwordless_auth_token.get_absolute_url(),
                },
                disable_antispam=True,
            )
        return Response(OkSerializer().data)


class ObtainJSONWebTokenViaPasswordlessToken(AnonymousAPIView):
    throttle_classes = [AuthAnonRateThrottle]

    @extend_schema(description="Exchange passwordless token to JWT", responses={200: TokenSerializer})
    def get(self, request: Request, token: str) -> Response:
        passwordless_auth_token = get_object_or_404(PasswordlessAuthToken.objects.valid(), token=token)

        passwordless_auth_token.mark_as_used()

        token = get_jwt(passwordless_auth_token.user)
        serializer = TokenSerializer({"token": token})
        return Response(serializer.data)


class ObtainJSONWebTokenViaUserId(APIView):
    permission_classes = [SuperUserOnly]

    @extend_schema(description="Get token for given user_id. Superuser only!", responses={200: TokenSerializer})
    def get(self, request: Request, user_id: str) -> Response:
        user = get_object_or_404(User, pk=user_id)
        token = get_jwt(user)
        serializer = TokenSerializer({"token": token})
        return Response(serializer.data)


class RequestPasswordResetView(dj_rest_auth_views.PasswordResetView):
    serializer_class = PasswordResetSerializer
