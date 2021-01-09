from typing import Iterable

from app.integrations.mailchimp.http import MailchimpHTTP
from app.integrations.mailchimp.member import MailchimpMember
from users.models import User


class AppMailchimp:
    def __init__(self):
        self.http = MailchimpHTTP()

    def subscribe_django_user(self, list_id: str, user: User):
        self.mass_subscribe(
            list_id=list_id,
            members=[
                MailchimpMember.from_django_user(user),
            ],
        )

    def mass_subscribe(self, list_id: str, members: Iterable[MailchimpMember]):

        member_list = list()
        for member in members:
            member_list.append({
                **member.to_mailchimp(),
                'status': 'subscribed',
            })

        return self.http.post(
            url=f'lists/{list_id}',
            payload={
                'members': member_list,
                'update_existing': True,
            },
        )


__all__ = [
    AppMailchimp,
]
