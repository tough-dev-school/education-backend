import pytest

from apps.a12n.models import JWTBlacklist

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def token(api):
    response = api.post(
        "/api/v2/auth/token/",
        {
            "username": api.user.username,
            "password": api.password,
        },
        format="json",
    )

    return response["token"]


@pytest.fixture
def user(api):
    return api.user


def test_non_blacklisted_token_query(anon, token, user):
    anon.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    got = anon.get("/api/v2/users/me/")

    assert got["id"] == user.id


def test_blacklisted_token_query(anon, token):
    JWTBlacklist.objects.create(token=token)
    anon.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    anon.get("/api/v2/users/me/", expected_status_code=401)
