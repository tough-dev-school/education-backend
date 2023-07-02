from typing import Iterator

from users.models import User


class ZoomusUser:
    """Proxy for user model to fit zoom.us participant requirements"""

    def __init__(self, user: User):
        self.user = user

    @property
    def first_name(self) -> str:
        """Sending space instead of last name if we dont know it"""
        return self.user.first_name or " "

    @property
    def last_name(self) -> str:
        """Sending space instead of last name if we dont know it"""
        return self.user.last_name or " "

    @property
    def email(self) -> str:
        return self.user.email

    def __iter__(self) -> Iterator[tuple[str, str]]:
        """Dictionary as accepted within zoom api"""
        yield from {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
        }.items()
