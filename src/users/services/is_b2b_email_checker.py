from dataclasses import dataclass
from typing import Callable, final

from django.core.validators import validate_email

from app.services import BaseService


@final
@dataclass
class IsB2BEmailChecker(BaseService):
    """
    Returns True if email is b2b and False if not
    """

    email: str

    CUSTOMER_DOMAINS = (
        "gmail.com",
        "icloud.com",
        "hotmail.com",
        "hey.com",
        "mail.ru",
        "list.ru",
        "bk.ru",
        "inbox.ru",
        "pm.me",
        "protonmail.com",
        "yandex.ru",
        "ya.ru",
        "rambler.ru",
        "riseup.net",
    )

    def act(self) -> bool:
        return self.email.split("@")[-1] not in self.CUSTOMER_DOMAINS

    def get_validators(self) -> list[Callable]:
        return [lambda: validate_email(self.email)]
