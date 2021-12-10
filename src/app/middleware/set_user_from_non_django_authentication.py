from typing import Callable, Optional

import contextlib
from django.contrib.auth.middleware import get_user
from django.utils.functional import SimpleLazyObject
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import APIException
from rest_framework.request import Request
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from users.models import User


class UserMiddleware:
    """Add authenticated user to the request object with some non-django authentication methods, like JWT or DRF token
    """
    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            request.user = SimpleLazyObject(lambda: self.get_user(request) or get_user(request))  # try ours get_user(), if fails -- django's stock one

        return self.get_response(request)

    @staticmethod
    def get_user(request: Request) -> Optional[User]:
        raise NotImplementedError('Please implement in subclass')


class JWTAuthMiddleware(UserMiddleware):
    @staticmethod
    def get_user(request: Request) -> Optional[User]:
        json_auth = JSONWebTokenAuthentication()

        with contextlib.suppress(APIException, TypeError):
            return json_auth.authenticate(request)[0]


class TokenAuthMiddleware(UserMiddleware):
    @staticmethod
    def get_user(request: Request) -> Optional[User]:
        token_authentication = TokenAuthentication()
        with contextlib.suppress(APIException, TypeError):
            return token_authentication.authenticate(request)[0]  # type: ignore
