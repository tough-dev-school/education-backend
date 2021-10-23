import pytest

from app.integrations.mailchimp.exceptions import MailchimpSubscriptionFailed

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def err_response(read_fixture):
    return read_fixture('app/tests/mailchimp/.fixtures/err_response')


@pytest.mark.parametrize('status', ['subscribed', 'unsubscribed'])
def test_single_member(mailchimp, post, mailchimp_member, status):
    mailchimp.mass_update_subscription(
        list_id='test1-list-id',
        members=[mailchimp_member],
        status=status,
    )

    post.assert_called_once_with(
        url='lists/test1-list-id',
        payload={
            'members': [
                {
                    'email_address': 'test@e.mail',
                    'merge_fields': {
                        'FNAME': 'Rulon',
                        'LNAME': 'Oboev',
                    },
                    'status': status,
                },
            ],
            'update_existing': True,
        },
    )


def test_spammers_error(mailchimp, mailchimp_member, err_response):
    """Integration test to validate an error is thrown when mailchimp returns error during subscription"""
    mailchimp.http_mock.post('https://us05.api.mailchimp.com/3.0/lists/test-list-id', json=err_response)

    with pytest.raises(MailchimpSubscriptionFailed) as exception:
        mailchimp.mass_update_subscription(
            list_id='test-list-id',
            members=[mailchimp_member],
            status='subscribed',
        )

    assert 'f+localmachinetest@f213.in has' in str(exception)
    assert '(ERROR_GENERIC)' in str(exception)
