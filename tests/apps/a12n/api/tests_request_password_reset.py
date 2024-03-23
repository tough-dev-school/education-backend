import pytest

pytestmark = [pytest.mark.django_db]


url = "/api/v2/auth/password/reset/"


@pytest.fixture(autouse=True)
def _set_frontend_url(settings):
    settings.FRONTEND_URL = "http://frontend"


@pytest.fixture(autouse=True)
def user(mixer):
    return mixer.blend("users.User", id=100500, first_name="Крякуш", last_name="Вольфрамов", email="test@email.com")


@pytest.fixture(autouse=True)
def _freeze_make_token(mocker):
    mocker.patch("django.contrib.auth.tokens.default_token_generator.make_token", return_value="__TOKEN__")


def test_request_reset_password_send_email_with_args(anon, send_mail):
    data = {
        "email": "test@email.com",
    }

    anon.post(url, data=data, expected_status_code=200)

    send_mail.assert_called_once_with(
        to="test@email.com",
        template_id="password-reset",
        disable_antispam=True,
        ctx={
            "name": "Крякуш Вольфрамов",
            "email": "test@email.com",
            "action_url": "http://frontend/auth/password/reset/MTAwNTAw/__TOKEN__/",
        },
    )


def test_send_nothing_if_user_not_exists(anon, send_mail):
    data = {
        "email": "not_existed_email@email.com",
    }

    anon.post(url, data=data, expected_status_code=200)

    send_mail.assert_not_called()


def test_uses_password_reset_form_template_id_settings(user, anon, settings, send_mail):
    settings.PASSWORD_RESET_TEMPLATE_ID = "new-reset-password-template_id"

    anon.post(url, data={"email": user.email}, expected_status_code=200)

    send_mail_kwargs = send_mail.call_args.kwargs
    assert send_mail_kwargs["template_id"] == "new-reset-password-template_id"
