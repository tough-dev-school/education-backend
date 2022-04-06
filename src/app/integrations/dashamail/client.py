from typing import Optional

from app.integrations.dashamail.exceptions import DashamailSubscriptionFailed
from app.integrations.dashamail.http import DashamailHTTP


class AppDashamail:
    def __init__(self) -> None:
        self.http = DashamailHTTP()

    def subscribe_user(self, list_id: str, email: str, first_name: str, last_name: str, tags: Optional[list[str]] = None) -> None:
        payload = {
            'method': 'lists.add_member',
            'update': True,
            'list_id': list_id,
            'email': email,
            'merge_1': first_name,
            'merge_2': last_name,
        }

        if tags:
            payload['merge_3'] = ';'.join(tags)

        response = self.http.post(
            url='',
            payload=payload,
        )

        if response['response']['msg']['err_code'] != 0:
            raise DashamailSubscriptionFailed(f'{response}')


__all__ = [
    'AppDashamail',
]
