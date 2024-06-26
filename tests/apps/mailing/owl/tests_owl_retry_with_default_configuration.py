from unittest.mock import Mock

import pytest
from anymail.exceptions import AnymailRequestsAPIError

from apps.mailing.owl import TemplateNotFoundError

pytestmark = [
    pytest.mark.django_db,
]

DEFAULT_BACKEND = "django.core.mail.backends.dummy.EmailBackend"
DEFAULT_FROM_EMAIL = "Donald T <trump@employee.trumphotels.com>"
DEFAULT_REPLY_TO = "Secretary of Donald T <support@trumphotels.com"


@pytest.fixture
def email_configuration(mixer):
    return mixer.blend("mailing.EmailConfiguration")


@pytest.fixture
def configuration(email_configuration, mocker):
    return mocker.patch("apps.mailing.owl.get_configuration", return_value=email_configuration)


@pytest.fixture(autouse=True)
def _settings(settings):
    settings.DEBUG = False
    settings.EMAIL_BACKEND = DEFAULT_BACKEND
    settings.DEFAULT_FROM_EMAIL = DEFAULT_FROM_EMAIL
    settings.DEFAULT_REPLY_TO = DEFAULT_REPLY_TO


@pytest.fixture
def mocked_send(mocker):
    return mocker.patch("anymail.message.AnymailMessage.send")


@pytest.fixture
def template_not_found_exception():
    return make_exception(
        data={"ErrorCode": 1101, "Message": "The Template's 'Alias' associated with this request is not valid or was not found."},
        status_code=422,
    )


def make_exception(data: dict, status_code: int = 422):
    response = Mock()
    response.status_code = status_code
    response.json.return_value = data

    return AnymailRequestsAPIError(response=response)


@pytest.mark.usefixtures("configuration")
def test_retry_with_default_configuration(owl, mocked_send, template_not_found_exception):
    sender = owl()
    mocked_send.side_effect = [template_not_found_exception, None]

    sender()

    assert mocked_send.call_count == 2


def test_doesnt_retry_if_first_call_was_with_default_configuration(owl, mocked_send, template_not_found_exception):
    mocked_send.side_effect = [template_not_found_exception, None]

    with pytest.raises(TemplateNotFoundError):
        owl()()

    assert mocked_send.call_count == 1


@pytest.mark.usefixtures("configuration")
def test_retry_with_default_configuration(owl, mocker):
    sender = owl()
    inner_send = mocker.patch.object(sender, "send")

    sender._retry_with_default_configuration(TemplateNotFoundError())

    inner_send.assert_called_once_with(sender.default_configuration)


def test_doesnt_send_with_different_error_code(owl, mocked_send):
    mocked_send.side_effect = make_exception(
        data={"ErrorCode": 1102, "Message": "The Template's 'Alias' associated with this request is not valid or was not found."},
        status_code=422,
    )

    with pytest.raises(AnymailRequestsAPIError):
        owl()()

    assert mocked_send.call_count == 1
