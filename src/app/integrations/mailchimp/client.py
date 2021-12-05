from typing import Iterable, Literal, Optional

from app.integrations.mailchimp import exceptions
from app.integrations.mailchimp.http import MailchimpHTTP
from app.integrations.mailchimp.member import MailchimpMember
from users.models import User


class AppMailchimp:
    def __init__(self):
        self.http = MailchimpHTTP()

    def subscribe_django_user(self, list_id: str, user: User, tags: Optional[Iterable] = None):
        member = MailchimpMember.from_django_user(user)
        self.mass_update_subscription(list_id=list_id, members=[member], status='subscribed')
        if tags is not None:
            self.set_tags(list_id=list_id, members=[member], tags=tags)

    def unsubscribe_django_user(self, list_id: str, user: User):
        member = MailchimpMember.from_django_user(user)
        self.mass_update_subscription(list_id=list_id, members=[member], status='unsubscribed')

    def mass_update_subscription(self, *, list_id: str, members: Iterable[MailchimpMember], status: Literal['subscribed', 'unsubscribed']):
        response = self.http.post(
            url=f'lists/{list_id}',
            payload={
                'members': [{**member.to_mailchimp(), 'status': status} for member in members],
                'update_existing': True,
            },
        )
        if len(response['errors']) > 0:
            raise exceptions.MailchimpSubscriptionFailed(', '.join([f'{err["email_address"]}: {err["error"]} ({err["error_code"]})' for err in response['errors']]))

    def set_tags(self, *, list_id: str, members: Iterable[MailchimpMember], tags: Iterable[str]):
        for member in members:
            self.http.post(
                url=f'/lists/{list_id}/members/{member.subscriber_hash}/tags',
                payload={
                    'tags': [{'name': tag, 'status': 'active'} for tag in tags],
                },
                expected_status_code=204,
            )


__all__ = [
    'AppMailchimp',
]
