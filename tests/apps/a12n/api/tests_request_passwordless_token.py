from datetime import datetime
from datetime import timedelta
from datetime import timezone
import pytest

from apps.a12n.models import PasswordlessAuthToken

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time("2049-01-05 12:45:44-04:00"),
]


@pytest.fixture(autouse=True)
def user(mixer):
    return mixer.blend("users.User", first_name="Secret", last_name="h4xx0r", email="zer0c00l@h4xx.net")


@pytest.fixture(autouse=True)
def _freeze_frontend_url(mocker):
    mocker.patch("apps.a12n.models.PasswordlessAuthToken.get_absolute_url", return_value="https://frontend/auth/__TOKEN__")


def test_token_is_created(anon, user):
    anon.get("/api/v2/auth/passwordless-token/request/zer0c00l@h4xx.net/")

    token = PasswordlessAuthToken.objects.last()

    assert token.user == user
    assert "-4" in str(token.token)
    assert token.expires == datetime(2049, 1, 5, 14, 45, 44, tzinfo=timezone(timedelta(hours=-4)))
    assert token.used is None


def test_email_is_sent(anon, send_mail):
    anon.get("/api/v2/auth/passwordless-token/request/zer0c00l@h4xx.net/")

    send_mail.assert_called_once_with(
        to="zer0c00l@h4xx.net",
        template_id="passwordless-token",
        ctx={
            "name": "Secret h4xx0r",
            "action_url": "https://frontend/auth/__TOKEN__",
        },
        disable_antispam=True,
    )


@pytest.mark.parametrize(
    "email",
    [
        "ev1l@nonexistant.user",
        " ",
    ],
)
def test_ev1l_user(anon, send_mail, email):
    anon.get(f"/api/v2/auth/passwordless-token/request/{email}/")

    assert PasswordlessAuthToken.objects.count() == 0
    send_mail.assert_not_called()


def test_email_case_sensitive(user, anon):
    anon.get("/api/v2/auth/passwordless-token/request/ZER0C00L@h4xx.net/")

    assert PasswordlessAuthToken.objects.count() == 0


def test_disabled_user_with_the_same_email_does_not_break_authentication(user, anon, mixer):
    mixer.blend("users.User", email=user.email, is_active=False)

    anon.get("/api/v2/auth/passwordless-token/request/zer0c00l@h4xx.net/")

    assert PasswordlessAuthToken.objects.last().user == user


def test_uses_passwordless_template_id_settings(user, anon, settings, send_mail):
    settings.PASSWORDLESS_TOKEN_TEMPLATE_ID = "new-passwordless-template-id"

    anon.get("/api/v2/auth/passwordless-token/request/zer0c00l@h4xx.net/")

    send_mail_kwargs = send_mail.call_args.kwargs
    assert send_mail_kwargs["template_id"] == "new-passwordless-template-id"
