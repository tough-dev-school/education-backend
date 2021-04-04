import json
import pytest

pytestmark = pytest.mark.django_db


@pytest.fixture
def get_token(api):
    def _get_token(username, password, expected_status_code=201):
        return api.post('/api/v2/auth/token/', {
            'username': username,
            'password': password,
        }, format='json', expected_status_code=expected_status_code)

    return _get_token


def _decode(response):
    return json.loads(response.content.decode('utf-8', errors='ignore'))


def test_getting_token_ok(api, get_token):
    got = get_token(api.user.username, api.password)

    assert 'token' in got


def test_getting_token_is_token(api, get_token):
    got = get_token(api.user.username, api.password)

    assert len(got['token']) > 32  # every stuff that is long enough, may be a JWT token


def test_getting_token_with_incorrect_password(api, get_token):
    got = get_token(api.user.username, 'z3r0c00l', expected_status_code=400)

    assert 'non_field_errors' in got


@pytest.mark.parametrize(('extract_token', 'status_code'), [
    (lambda response: response['token'], 200),
    (lambda *args: 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6InRpbW90aHk5NSIsImlhdCI6MjQ5MzI0NDgwMCwiZXhwIjoyNDkzMjQ1MTAwLCJqdGkiOiI2MWQ2MTE3YS1iZWNlLTQ5YWEtYWViYi1mOGI4MzBhZDBlNzgiLCJ1c2VyX2lkIjoxLCJvcmlnX2lhdCI6MjQ5MzI0NDgwMH0.YQnk0vSshNQRTAuq1ilddc9g3CZ0s9B0PQEIk5pWa9I', 401),
    (lambda *args: 'sh1t', 401),
])
def test_received_token_works(api, get_token, anon, extract_token, status_code):
    token = extract_token(get_token(api.user.username, api.password))

    anon.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    anon.get('/api/v2/users/me/', expected_status_code=status_code)
