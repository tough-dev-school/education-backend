from typing import Optional

from dataclasses import dataclass

from users.models import User


@dataclass
class DashamailMember:
    email: str
    first_name: str
    last_name: str
    tags: Optional[list[str]] = None

    def to_dashamail(self) -> dict:
        member = {
            'email': self.email,
            'merge_1': self.first_name,
            'merge_2': self.last_name,
        }
        if self.tags:
            member['merge_3'] = ';'.join(self.tags)

        return member

    @classmethod
    def from_django_user(cls, user: User):
        return cls(
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
        )
