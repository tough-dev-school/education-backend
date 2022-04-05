import pytest

from app.integrations.dashamail.exceptions import DashamailWrongResponse

pytestmark = [pytest.mark.django_db]


def test_post_ok(dashamail, successful_response_json):
    dashamail.http_mock.post('https://api.dashamail.com', json=successful_response_json)

    assert dashamail.http.post('', payload={}) == successful_response_json


def test_post_no_content(dashamail):
    dashamail.http_mock.post('https://api.dashamail.com/test/')

    with pytest.raises(DashamailWrongResponse):
        assert dashamail.http.post('test/', payload={})


def test_post_wrong_status_code(dashamail, successful_response_json):
    dashamail.http_mock.post('https://api.dashamail.com/test/', json=successful_response_json, status_code=500)

    with pytest.raises(DashamailWrongResponse):
        dashamail.http.post('test/', payload={})


def test_post_payload(dashamail, successful_response_json):
    def assertion(request, context):
        assert '__mocked=test' in request.text

        return successful_response_json

    dashamail.http_mock.post('https://api.dashamail.com/test/', json=assertion)

    dashamail.http.post('test/', payload={
        '__mocked': 'test',
    })


@pytest.mark.xfail(strict=True, reason='Just to check above test works')
def test_post_payload_fail(dashamail, successful_response_json):
    def assertion(request, context):
        assert '__mocked=not_test' in request.text

        return successful_response_json

    dashamail.http_mock.post('https://api.dashamail.com/test/', json=assertion)

    dashamail.http.post('test/', payload={
        '__mocked': 'test',
    })


def test_api_key_in_payload(dashamail, successful_response_json):
    def assertion(request, context):
        assert 'api_key=apikey' in request.text

        return successful_response_json

    dashamail.http_mock.post('https://api.dashamail.com/test/', json=assertion)

    dashamail.http.post('test/', payload={})
