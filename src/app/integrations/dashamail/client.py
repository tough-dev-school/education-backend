from typing import Iterable, Optional

from app.integrations.dashamail.exceptions import DashamailSubscriptionFailed
from app.integrations.dashamail.http import DashamailHTTP
from app.integrations.dashamail.member import DashamailMember
from users.models import User


class AppDashamail:
    def __init__(self) -> None:
        self.http = DashamailHTTP()

    def subscribe_django_user(self, list_id: str, user: User, tags: Optional[Iterable] = None) -> None:
        member = DashamailMember.from_django_user(user)
        if tags is not None:
            member.tags = tags
        self.update_subscription(list_id=list_id, member=member)

    def unsubscribe_django_user(self, list_id: str, user: User) -> None:
        self.http.post(
            url='',
            payload={
                'method': 'lists.unsubscribe_member',
                'email': user.email,
                'list_id': list_id,
            },
        )

    def update_subscription(self, list_id: str, member: DashamailMember) -> None:
        response = self.http.post(
            url='',
            payload={
                **member.to_dashamail(),
                'method': 'lists.add_member',
                'update': True,
                'list_id': list_id,
            },
        )

        if response['response']['msg']['err_code'] != 0:
            raise DashamailSubscriptionFailed(f'{response}')


__all__ = [
    'AppDashamail',
]
