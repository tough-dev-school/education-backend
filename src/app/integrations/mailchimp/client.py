from typing import Iterable

from app.integrations.mailchimp.http import MailchimpHTTP
from app.integrations.mailchimp.member import MailchimpMember


class AppMailchimp:
    def __init__(self):
        self.http = MailchimpHTTP()

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
