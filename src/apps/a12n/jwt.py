import jwt
from django.utils.translation import gettext_lazy as _
from drf_spectacular.contrib.rest_framework_jwt import JWTScheme
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.utils import jwt_create_payload

from apps.a12n.models import JWTBlacklist
from apps.users.models import User


def payload_handler(user: User) -> dict:
    """Add app-wide payload to generated JWT's"""
    return {
        **jwt_create_payload(user),
        "user_public_id": user.uuid,
    }


def decode_jwt_without_validation(token: str) -> dict:
    return jwt.decode(token, options={"verify_signature": False}, algorithms=["RS256"])


class AppJSONWebTokenAuthentication(JSONWebTokenAuthentication):
    """Custom JWT Blacklisting, cuz bundled with rest_framework_jwt is too complicated"""

    def authenticate(self, request: Request) -> tuple[User, str] | None:
        authentication_result = super().authenticate(request)
        if authentication_result is None:
            return None

        token = self.get_token_from_request(request)
        if token is None:
            return None

        if JWTBlacklist.objects.filter(token=token).exists():
            raise AuthenticationFailed(_("Invalid token."))

        return authentication_result


class AppJSONWebTokenAuthenticationScheme(JWTScheme):  # type: ignore
    """Mimic JWT description, bundled in drf_spectacular"""

    target_class = "apps.a12n.jwt.AppJSONWebTokenAuthentication"
