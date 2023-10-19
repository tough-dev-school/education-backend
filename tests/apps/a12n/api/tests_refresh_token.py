import pytest

from freezegun import freeze_time

from apps.a12n.utils import get_jwt

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time("2049-01-05"),
]


@pytest.fixture
def refresh_token(api):
    def _refresh_token(token, expected_status_code=201):
        return api.post(
            "/api/v2/auth/token/refresh/",
            {
                "token": token,
            },
            format="json",
            expected_status_code=expected_status_code,
        )

    return _refresh_token


@pytest.fixture
def initial_token(api):
    with freeze_time("2049-01-03"):
        return get_jwt(api.user)


def test_refresh_token_ok(initial_token, refresh_token):
    got = refresh_token(initial_token)

    assert "token" in got


def test_refreshed_token_is_a_token(initial_token, refresh_token):
    got = refresh_token(initial_token)

    assert len(got["token"]) > 32


def test_refreshed_token_is_new_one(initial_token, refresh_token):
    got = refresh_token(initial_token)

    assert got["token"] != initial_token


def test_refresh_token_fails_with_incorrect_previous_token(refresh_token):
    got = refresh_token("some-invalid-previous-token", expected_status_code=400)

    assert "non_field_errors" in got


def test_token_is_not_allowed_to_refresh_if_expired(initial_token, refresh_token):
    with freeze_time("2049-02-05"):
        got = refresh_token(initial_token, expected_status_code=400)

    assert "expired" in got["non_field_errors"][0]


def test_received_token_works(anon, refresh_token, initial_token):
    token = refresh_token(initial_token)["token"]

    anon.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    got = anon.get("/api/v2/users/me/")

    assert got is not None
