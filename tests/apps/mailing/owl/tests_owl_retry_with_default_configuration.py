from unittest.mock import Mock

import pytest
from anymail.exceptions import AnymailRequestsAPIError

pytestmark = [
    pytest.mark.django_db,
]

DEFAULT_BACKEND = "django.core.mail.backends.dummy.EmailBackend"
DEFAULT_FROM_EMAIL = "Donald T <trump@employee.trumphotels.com>"
DEFAULT_REPLY_TO = "Secretary of Donald T <support@trumphotels.com"


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


def test_retry_with_default_configuration(owl, mocked_send, template_not_found_exception):
    sender = owl()
    mocked_send.side_effect = [template_not_found_exception, None]

    sender()

    assert sender.backend_name == DEFAULT_BACKEND
    assert sender.msg.from_email == DEFAULT_FROM_EMAIL
    assert sender.msg.reply_to == [DEFAULT_REPLY_TO]


def test_raises_if_retry_raised(owl, mocked_send, template_not_found_exception):
    mocked_send.side_effect = [template_not_found_exception, template_not_found_exception]

    with pytest.raises(AnymailRequestsAPIError):
        owl()()

    assert mocked_send.call_count == 2


def test_doesnt_send_with_different_error_code(owl, mocked_send):
    mocked_send.side_effect = make_exception(
        data={"ErrorCode": 1102, "Message": "The Template's 'Alias' associated with this request is not valid or was not found."},
        status_code=422,
    )

    with pytest.raises(AnymailRequestsAPIError):
        owl()()

    assert mocked_send.call_count == 1
