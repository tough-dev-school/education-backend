import pytest

from apps.a12n.jwt import decode_jwt_without_validation
from apps.users.services import UserCreator

pytestmark = pytest.mark.django_db


@pytest.fixture
def get_token(api):
    def _get_token(username, password, expected_status_code=201):
        return api.post(
            "/api/v2/auth/token/",
            {
                "username": username,
                "password": password,
            },
            format="json",
            expected_status_code=expected_status_code,
        )

    return _get_token


def test_getting_token_ok(api, get_token):
    got = get_token(api.user.username, api.password)

    assert "token" in got


def test_getting_token_by_email(user, get_token):
    user = UserCreator(name="lol bar", email="lolbar@example.com")()
    user.set_password("123456")
    user.save()

    got = get_token("lolbar@example.com", "123456")

    assert "token" in got


def test_getting_token_case_sensitive_email(get_token):
    user = UserCreator(name="lol bar", email="lolbar@example.com")()
    user.set_password("123456")
    user.save()

    got2 = get_token("LOLBAR@EXAMPLE.Com", "123456", expected_status_code=400)

    assert "non_field_errors" in got2


def test_getting_token_case_sensitive_username(get_token, mixer):
    user = mixer.blend("users.User", username="Jimbo", email="jimbo@example.com")
    user.set_password("123456")
    user.save()

    got2 = get_token("jimbo", "123456", expected_status_code=400)
    assert "non_field_errors" in got2


def test_getting_token_is_a_token(api, get_token):
    got = get_token(api.user.username, api.password)

    payload = decode_jwt_without_validation(got["token"])

    assert payload["iss"] == "education-backend"
    assert payload["user_public_id"] == str(api.user.uuid)


def test_getting_token_with_incorrect_password(api, get_token):
    got = get_token(api.user.username, "z3r0c00l", expected_status_code=400)

    assert "non_field_errors" in got


def test_getting_token_when_banned_by_axes(api, get_token, settings):
    settings.AXES_FAILURE_LIMIT = 0

    got = get_token(api.user.username, api.password, expected_status_code=403)

    assert got == {"detail": "Too many failed login attempts"}


@pytest.mark.parametrize(
    ("extract_token", "status_code"),
    [
        (lambda response: response["token"], 200),
        (
            lambda *args: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6InRpbW90aHk5NSIsImlhdCI6MjQ5MzI0NDgwMCwiZXhwIjoyNDkzMjQ1MTAwLCJqdGkiOiI2MWQ2MTE3YS1iZWNlLTQ5YWEtYWViYi1mOGI4MzBhZDBlNzgiLCJ1c2VyX2lkIjoxLCJvcmlnX2lhdCI6MjQ5MzI0NDgwMH0.YQnk0vSshNQRTAuq1ilddc9g3CZ0s9B0PQEIk5pWa9I",
            401,
        ),
        (lambda *args: "sh1t", 401),
    ],
)
def test_received_token_works(api, get_token, anon, extract_token, status_code):
    token = extract_token(get_token(api.user.username, api.password))

    anon.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    anon.get("/api/v2/users/me/", expected_status_code=status_code)
