import pytest

from app.integrations.mailchimp import AppMailchimpWrongResponseException

pytestmark = [pytest.mark.django_db]

MEMBERS_URL = 'https://us05.api.mailchimp.com/3.0/lists/123cba/members'


@pytest.mark.usefixtures('member_is_always_new')
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
@pytest.mark.usefixtures('member_is_always_new')
def test_fail(user, mailchimp):
    def assertions(request, context):
        req = request.json()

        assert req['email_address'] == 'wrong@email.com'

    mailchimp.http_mock.post(MEMBERS_URL, json=assertions)

    mailchimp.subscribe(user)


@pytest.mark.usefixtures('member_is_always_new')
def test_exception(user, mailchimp):
    mailchimp.http_mock.post(MEMBERS_URL, json={'test': True}, status_code=405)

    with pytest.raises(AppMailchimpWrongResponseException):
        mailchimp.subscribe(user)


@pytest.mark.parametrize('member_exists_response, call_count', [
    (True, 0),
    (False, 1),
])
def test_user_is_not_subscribed_when_it_already_exists(user, mailchimp, subscribe, member_exists, member_exists_response, call_count):
    member_exists.return_value = member_exists_response

    mailchimp.subscribe(user)

    assert subscribe.call_count == call_count
