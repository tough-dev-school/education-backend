import pytest

from app.integrations.mailchimp import AppMailchimpWrongResponseException

pytestmark = [pytest.mark.django_db]


MEMBER_URL = 'https://us05.api.mailchimp.com/3.0/lists/123cba/members/{subscriber_hash}'
USER_HASH = 'bac8eb22f0ed07fa57fa5000117fc3de'  # md5 of test@e.mail


@pytest.mark.parametrize('response, user_exists', [
    (404, False),
    (200, True),
])
def test(user, mailchimp, response, user_exists):
    mailchimp.http_mock.get(MEMBER_URL.format(subscriber_hash=USER_HASH), status_code=response, json=dict())

    assert mailchimp.member_exists('test@e.mail') is user_exists


def test_other_exceptions_are_raised_ok(user, mailchimp):
    mailchimp.http_mock.get(MEMBER_URL.format(subscriber_hash=USER_HASH), status_code=400, json=dict())

    with pytest.raises(AppMailchimpWrongResponseException):
        mailchimp.member_exists('test@e.mail')
