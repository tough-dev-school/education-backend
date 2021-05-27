from ipaddress import IPv4Address, IPv4Network
from rest_framework import permissions


class TinkoffCreditNetmaskPermission(permissions.BasePermission):
    """The only way to validate webhooks from tinkoff credit is IP addess,
    proof: https://forma.tinkoff.ru/docs/credit/help/http/
    """
    message = 'Tinkoff Credit requests are allowed only from tinkoff network'

    def has_permission(self, request, *args, **kwargs):
        sender_ip = IPv4Address(request.META['REMOTE_ADDR'])

        return sender_ip in IPv4Network('91.194.226.0/23')
