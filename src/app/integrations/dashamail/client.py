from typing import Optional

from app.integrations.dashamail.exceptions import DashamailSubscriptionFailed
from app.integrations.dashamail.http import DashamailHTTP
from app.integrations.dashamail.member import DashamailMember


class AppDashamail:
    def __init__(self) -> None:
        self.http = DashamailHTTP()

    def subscribe_user(self, list_id: str, email: str, first_name: str, last_name: str, tags: Optional[list[str]] = None) -> None:
        member = DashamailMember(email, first_name, last_name, tags)
        self.update_subscription(list_id=list_id, member=member)

    def unsubscribe_user(self, list_id: str, email: str) -> None:
        self.http.post(
            url='',
            payload={
                'method': 'lists.unsubscribe_member',
                'email': email,
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
