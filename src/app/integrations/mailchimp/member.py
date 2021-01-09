import hashlib
from dataclasses import dataclass

from users.models import User


@dataclass
class MailchimpMember:
    email: str
    first_name: str
    last_name: str

    @property
    def subscriber_hash(self) -> str:
        return hashlib.md5(self.email.lower().encode()).hexdigest()

    def to_mailchimp(self) -> dict:
        return {
            'email_address': self.email,
            'merge_fields': {
                'FNAME': self.first_name,
                'LNAME': self.last_name,
            },
        }

    @classmethod
    def from_django_user(cls, user: User):
        return cls(
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
        )
