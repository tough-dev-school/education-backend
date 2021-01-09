import pytest

from app.integrations.mailchimp.client import MailchimpMember

pytestmark = [pytest.mark.django_db]


def test_single_member(mailchimp, post):
    mailchimp.mass_subscribe(
        list_id='test1-list-id',
        members=[
            MailchimpMember(email='test@1.org', first_name='Kamaz', last_name='Otkhodov'),
        ],
    )

    post.assert_called_once_with(
        url='lists/test1-list-id',
        payload={
            'members': [{
                'email_address': 'test@1.org',
                'merge_fields': {
                    'FNAME': 'Kamaz',
                    'LNAME': 'Otkhodov',
                },
                'status': 'subscribed',
            }],
            'update_existing': True,
        },
    )


def test_two_members(mailchimp, post):
    mailchimp.mass_subscribe(
        list_id='test1-list-id',
        members=[
            MailchimpMember(email='test@1.org', first_name='Kamaz', last_name='Otkhodov'),
            MailchimpMember(email='test@2.org', first_name='Rulon', last_name='Oboev'),
        ],
    )

    post.assert_called_once_with(
        url='lists/test1-list-id',
        payload={
            'members': [{
                'email_address': 'test@1.org',
                'merge_fields': {
                    'FNAME': 'Kamaz',
                    'LNAME': 'Otkhodov',
                },
                'status': 'subscribed',
            }, {
                'email_address': 'test@2.org',
                'merge_fields': {
                    'FNAME': 'Rulon',
                    'LNAME': 'Oboev',
                },
                'status': 'subscribed',
            }],
            'update_existing': True,
        },
    )
