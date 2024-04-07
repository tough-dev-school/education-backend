import pytest
from django.contrib.auth.hashers import check_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

pytestmark = [pytest.mark.django_db]


url = "/api/v2/auth/password/reset/confirm/"


@pytest.fixture
def get_confirm_payload(user):
    return lambda _new_password1, _new_password2=None: {
        "new_password1": _new_password1,
        "new_password2": _new_password2 or _new_password1,
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": default_token_generator.make_token(user),
    }


def test_password_actually_was_reset(anon, user, get_confirm_payload):
    data = get_confirm_payload("new_strong_password")

    anon.post(url, data=data, expected_status_code=200)

    user.refresh_from_db()
    assert check_password("new_strong_password", user.password)


@pytest.mark.parametrize(
    "password",
    [
        "small",
        "12345678910",
    ],
)
def test_basic_password_strength_validation(anon, password, get_confirm_payload):
    data = get_confirm_payload(password)

    got = anon.post(url, data=data, expected_status_code=400)
    assert "new_password2" in got


def test_error_when_new_passwords_mismatch(anon, get_confirm_payload):
    data = get_confirm_payload("new_strong_password", "mismatched_password")

    got = anon.post(url, data=data, expected_status_code=400)

    assert "new_password2" in got


def test_same_token_couldnt_be_used_twice(anon, get_confirm_payload):
    data = get_confirm_payload("new_strong_password")
    anon.post(url, data=data, expected_status_code=200)

    got = anon.post(url, data=data, expected_status_code=400)
    assert "token" in got
