import json
import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def token(user, mixer):
    return mixer.blend('a12n.PasswordlessAuthToken', user=user, token='3149798e-c219-47f5-921f-8ae9a75b709b')


@pytest.fixture
def get_token(api):
    def _get_token(token, expected_status_code=200):
        return api.get(f'/api/v2/auth/passwordless-token/{token}/', expected_status_code=expected_status_code)

    return _get_token


def _decode(response):
    return json.loads(response.content.decode('utf-8', errors='ignore'))


def test_invalid_token(get_token):
    get_token('1nvalid', expected_status_code=404)


def test_valid_token(get_token, token):
    got = get_token(token=str(token.token))

    assert len(got['token']) > 32  # every stuff that is long enough, may be a JWT token


@pytest.mark.parametrize(('extract_token', 'status_code'), [
    (lambda response: response['token'], 200),
    (lambda *args: 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6InRpbW90aHk5NSIsImlhdCI6MjQ5MzI0NDgwMCwiZXhwIjoyNDkzMjQ1MTAwLCJqdGkiOiI2MWQ2MTE3YS1iZWNlLTQ5YWEtYWViYi1mOGI4MzBhZDBlNzgiLCJ1c2VyX2lkIjoxLCJvcmlnX2lhdCI6MjQ5MzI0NDgwMH0.YQnk0vSshNQRTAuq1ilddc9g3CZ0s9B0PQEIk5pWa9I', 401),
    (lambda *args: 'sh1t', 401),
])
def test_received_token_works(api, get_token, anon, token, extract_token, status_code):
    token = extract_token(get_token(token=str(token.token)))

    anon.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    anon.get('/api/v2/users/me/', expected_status_code=status_code)
