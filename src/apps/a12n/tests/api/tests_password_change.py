import pytest
from django.contrib.auth.hashers import check_password

pytestmark = [pytest.mark.django_db]


url = "/api/v2/auth/password/change/"


def test_password_actually_changed(as_user, user):
    data = {
        "new_password1": "prefer_use_1password",
        "new_password2": "prefer_use_1password",
    }

    as_user.post(url, data=data, expected_status_code=200)

    user.refresh_from_db()
    assert check_password("prefer_use_1password", user.password) is True


@pytest.mark.parametrize(
    "password",
    [
        "small",  # forbid too small
        "123458910",  # forbid numeric only
    ],
)
def test_basic_password_strength_validation(as_user, password):
    data = {
        "new_password1": password,
        "new_password2": password,
    }

    as_user.post(url, data=data, expected_status_code=400)


def test_anon_forbidden(anon):
    anon.post(url, data={}, expected_status_code=401)
