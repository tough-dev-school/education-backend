import pytest

from app.integrations.mailchimp.http import MailChimpNotFound, MailChimpWrongResponse

pytestmark = [pytest.mark.django_db]


def test_get_ok(mailchimp):
    mailchimp.http_mock.get('https://us05.api.mailchimp.com/3.0/test/endpoint', json={'ok': True})

    assert mailchimp.http.get('test/endpoint') == {'ok': True}


def test_custom_status_code(mailchimp):
    mailchimp.http_mock.get('https://us05.api.mailchimp.com/3.0/test/endpoint', json={'ok': True}, status_code=204)

    assert mailchimp.http.request(url='test/endpoint', method='GET', expected_status_code=204) == {'ok': True}


def test_custom_status_code_fail(mailchimp):
    mailchimp.http_mock.get('https://us05.api.mailchimp.com/3.0/test/endpoint', json={'ok': True}, status_code=200)

    with pytest.raises(MailChimpWrongResponse):
        mailchimp.http.request(method='GET', url='test/endpoint', expected_status_code=931)


def test_get_no_content(mailchimp):
    mailchimp.http_mock.get('https://us05.api.mailchimp.com/3.0/test/endpoint')

    assert mailchimp.http.get('test/endpoint') is None


def test_post_ok(mailchimp):
    mailchimp.http_mock.post('https://us05.api.mailchimp.com/3.0/test/endpoint', json={'ok': True})

    assert mailchimp.http.post('test/endpoint', payload=dict()) == {'ok': True}


def test_post_no_content(mailchimp):
    mailchimp.http_mock.post('https://us05.api.mailchimp.com/3.0/test/endpoint')

    assert mailchimp.http.post('test/endpoint', payload=dict()) is None


@pytest.mark.parametrize(('code', 'exception'), [
    (504, MailChimpWrongResponse),
    (404, MailChimpNotFound),
])
def test_get_wrong_status_codes(mailchimp, code, exception):
    mailchimp.http_mock.get('https://us05.api.mailchimp.com/3.0/test/endpoint', json={'ok': True}, status_code=code)

    with pytest.raises(exception):
        mailchimp.http.get('test/endpoint')


@pytest.mark.parametrize(('code', 'exception'), [
    (504, MailChimpWrongResponse),
    (404, MailChimpNotFound),
])
def test_post_wrong_status_codes(mailchimp, code, exception):
    mailchimp.http_mock.post('https://us05.api.mailchimp.com/3.0/test/endpoint', json={'ok': True}, status_code=code)

    with pytest.raises(exception):
        mailchimp.http.post('test/endpoint', payload=dict())


def test_post_payload(mailchimp):
    def assertion(request, context):
        json = request.json()

        assert json['__mocked'] == 'test'

        return {'ok': True}

    mailchimp.http_mock.post('https://us05.api.mailchimp.com/3.0/test/endpoint', json=assertion)

    mailchimp.http.post('test/endpoint', payload={
        '__mocked': 'test',
    })


@pytest.mark.xfail(strict=True, reason='Just to check above test works')
def test_post_payload_fail(mailchimp):
    def assertion(request, context):
        json = request.json()

        assert json['__mocked'] == 'SHOULD NOT BE MOCKED'

        return {'ok': True}

    mailchimp.http_mock.post('https://us05.api.mailchimp.com/3.0/test/endpoint', json=assertion)

    mailchimp.http.post('test/endpoint', payload={
        '__mocked': 'test',
    })


def test_authentication(mailchimp):
    def assertion(request, context):
        assert request.headers['Authorization'] == 'Basic dXNlcjprZXktdXMwNQ=='

        return {'ok': True}

    mailchimp.http_mock.get('https://us05.api.mailchimp.com/3.0/test/endpoint', json=assertion)

    mailchimp.http.get('test/endpoint')


@pytest.mark.xfail(strict=True, reason='Just to check above test works')
def test_authentication_wr0ng(mailchimp):
    def assertion(request, context):
        assert request.headers['Authorization'] == 'UNKNOWN AUTH DO NOT WORK'

        return {'ok': True}

    mailchimp.http_mock.get('https://us05.api.mailchimp.com/3.0/test/endpoint', json=assertion)

    mailchimp.http.get('test/endpoint')
