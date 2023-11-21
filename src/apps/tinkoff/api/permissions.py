from ipaddress import IPv4Address
from ipaddress import IPv4Network
from typing import Any

from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView


class DolyameNetmaskPermission(permissions.BasePermission):
    """The only way to validate webhooks from dolyame is IP addess,
    proof: https://dolyame.ru/develop/help/webhooks/
    """

    message = "Dolyament requests are allowed only from apps.tinkoff network"

    def has_permission(self, request: Request, view: APIView, *args: Any, **kwargs: dict[str, Any]) -> bool:
        sender_ip = IPv4Address(request.META["REMOTE_ADDR"])

        return sender_ip in IPv4Network("91.194.226.0/23")
