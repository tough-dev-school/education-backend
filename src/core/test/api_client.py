import json
import random
import string
from typing import Any

from mixer.backend.django import mixer
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.test import APIClient

from apps.users.models import User


class DRFClient(APIClient):
    def __init__(
        self,
        user: User | None = None,
        god_mode: bool = True,
        anon: bool = False,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)

        if not anon:
            self.auth(user, god_mode)

    def auth(self, user: User | None = None, god_mode: bool = True) -> None:
        self.user = user or self._create_user(god_mode)
        self.god_mode = god_mode

        token = Token.objects.get_or_create(user=self.user)[0]
        self.credentials(
            HTTP_AUTHORIZATION=f"Token {token}",
        )

    def _create_user(self, god_mode: bool = True) -> User:
        user_opts = {}
        if god_mode:
            user_opts = {
                "is_staff": False,
                "is_superuser": True,
            }
        user = mixer.blend("users.User", **user_opts)
        self.password = "".join([random.choice(string.hexdigits) for _ in range(6)])
        user.set_password(self.password)
        user.save()
        return user

    def logout(self) -> None:
        self.credentials()
        super().logout()

    def get(self, *args: Any, **kwargs: Any) -> dict | Response:  # type: ignore[override]
        return self._api_call("get", kwargs.get("expected_status_code", 200), *args, **kwargs)

    def post(self, *args: Any, **kwargs: Any) -> dict | Response:  # type: ignore[override]
        return self._api_call("post", kwargs.get("expected_status_code", 201), *args, **kwargs)

    def put(self, *args: Any, **kwargs: Any) -> dict | Response:  # type: ignore[override]
        return self._api_call("put", kwargs.get("expected_status_code", 200), *args, **kwargs)

    def patch(self, *args: Any, **kwargs: Any) -> dict | Response:  # type: ignore[override]
        return self._api_call("patch", kwargs.get("expected_status_code", 200), *args, **kwargs)

    def delete(self, *args: Any, **kwargs: Any) -> dict | Response:  # type: ignore[override]
        return self._api_call("delete", kwargs.get("expected_status_code", 204), *args, **kwargs)

    def _api_call(self, method: str, expected: int, *args: Any, **kwargs: Any) -> dict | Response:
        kwargs["format"] = kwargs.get("format", "json")  # by default submit all data in JSON
        as_response = kwargs.pop("as_response", False)

        method = getattr(super(), method)
        response = method(*args, **kwargs)  # type: ignore[operator]

        if as_response:
            return response

        content = self._decode(response)

        assert response.status_code == expected, f'Got {response.status_code} instead of {expected}. Content is "{content}"'

        return content

    def _decode(self, response: Response) -> dict | Response:
        content = response.content.decode("utf-8", errors="ignore")
        if self.is_json(response):
            return json.loads(content)
        else:
            return content

    @staticmethod
    def is_json(response: Response) -> bool:
        if response.has_header("content-type"):
            return "json" in response.get("content-type", "")

        return False
