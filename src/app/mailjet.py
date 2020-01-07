import mailjet_rest as mailjet
from django.conf import settings
from django.utils.functional import cached_property

from users.models import User


class AppMailjetWrongResponseException(Exception):
    pass


class AppMailjet:
    def __init__(self):
        pass

    @cached_property
    def client(self):
        return mailjet.Client(
            auth=(settings.MAILJET_API_KEY, settings.MAILJET_SECRET_KEY),
            version='v3',
        )

    def subscribe(self, user: User, list_id: int):
        response = self.client.contactslist_managecontact.create(
            id=list_id,
            data={
                'Action': 'addnoforce',
                'Email': user.email,
                'Properties': {
                    'name': str(user),
                    'firstname': user.first_name,
                    'lastname': user.last_name,
                },
            },
        )

        if response.status_code != 201:
            raise AppMailjetWrongResponseException(f'Wrong response from mailjet: {response.status_code}. Content: {response.content}')
