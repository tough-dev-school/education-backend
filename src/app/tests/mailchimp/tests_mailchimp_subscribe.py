import pytest

from app.integrations.mailchimp import AppMailchimpWrongResponseException

pytestmark = [pytest.mark.django_db]

MEMBERS_URL = 'https://us05.api.mailchimp.com/3.0/lists/123cba/members'


def test(user, mailchimp):
    def assertions(request, context):
        req = request.json()

        assert req['email_address'] == 'test@e.mail'
        assert req['status'] == 'subscribed'
        assert req['merge_fields']['FNAME'] == 'Rulon'
        assert req['merge_fields']['LNAME'] == 'Oboev'

    mailchimp.http_mock.post(MEMBERS_URL, json=assertions)

    mailchimp.subscribe(user)


@pytest.mark.xfail(strict=True, reason='Just to make sure above test works')
def test_fail(user, mailchimp):
    def assertions(request, context):
        req = request.json()

        assert req['email_address'] == 'wrong@email.com'

    mailchimp.http_mock.post(MEMBERS_URL, json=assertions)

    mailchimp.subscribe(user)


def test_exception(user, mailchimp):
    mailchimp.http_mock.post(MEMBERS_URL, json={'test': True}, status_code=405)

    with pytest.raises(AppMailchimpWrongResponseException):
        mailchimp.subscribe(user)
