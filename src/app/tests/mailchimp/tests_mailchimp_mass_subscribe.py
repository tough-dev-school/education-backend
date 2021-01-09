import pytest

pytestmark = [pytest.mark.django_db]


def test_single_member(mailchimp, post, mailchimp_member):
    mailchimp.mass_subscribe(
        list_id='test1-list-id',
        members=[mailchimp_member],
    )

    post.assert_called_once_with(
        url='lists/test1-list-id',
        payload={
            'members': [{
                'email_address': 'test@e.mail',
                'merge_fields': {
                    'FNAME': 'Rulon',
                    'LNAME': 'Oboev',
                },
                'status': 'subscribed',
            }],
            'update_existing': True,
        },
    )
