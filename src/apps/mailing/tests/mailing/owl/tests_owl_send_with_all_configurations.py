from unittest.mock import Mock, call

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
def ya_email_configuration(mixer):
    return mixer.blend("mailing.EmailConfiguration")


@pytest.fixture
def configurations(email_configuration, mocker):
    return mocker.patch("apps.mailing.owl.get_configurations", return_value=[email_configuration])


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


def test_uses_default_configuration_if_theres_no_configurations(owl, configurations, mocked_send, template_not_found_exception):
    configurations.return_value = []
    sender = owl()
    mocked_send.side_effect = [template_not_found_exception, None]

    with pytest.raises(TemplateNotFoundError):
        sender()

    assert mocked_send.call_count == 1


@pytest.mark.usefixtures("configurations")
def test_sends_second_time_if_first_raised(owl, mocked_send, template_not_found_exception):
    sender = owl()
    mocked_send.side_effect = [template_not_found_exception, None]

    sender()

    assert mocked_send.call_count == 2


@pytest.mark.usefixtures("configurations")
def test_raises_if_no_configurations_left(owl, mocked_send, template_not_found_exception):
    sender = owl()
    mocked_send.side_effect = [template_not_found_exception, template_not_found_exception]

    with pytest.raises(TemplateNotFoundError):
        sender()

    assert mocked_send.call_count == 2


def test_doesnt_retry_if_first_call_was_with_default_configuration(owl, mocked_send, template_not_found_exception):
    mocked_send.side_effect = [template_not_found_exception, None]

    with pytest.raises(TemplateNotFoundError):
        owl()()

    assert mocked_send.call_count == 1


def test_uses_all_configurations_and_sends(owl, mocker, configurations, email_configuration, ya_email_configuration):
    configurations.return_value = [email_configuration, ya_email_configuration]
    sender = owl()
    inner_send = mocker.patch.object(sender, "send")
    inner_send.side_effect = [TemplateNotFoundError(), TemplateNotFoundError(), None]

    sender()

    inner_send.assert_has_calls(
        [
            call(email_configuration),
            call(ya_email_configuration),
            call(sender.default_configuration),
        ]
    )


def test_uses_all_configurations_and_raises(owl, mocker, configurations, email_configuration, ya_email_configuration):
    configurations.return_value = [email_configuration, ya_email_configuration]
    sender = owl()
    inner_send = mocker.patch.object(sender, "send")
    inner_send.side_effect = [TemplateNotFoundError(), TemplateNotFoundError(), TemplateNotFoundError()]

    with pytest.raises(TemplateNotFoundError):
        sender()

    inner_send.assert_has_calls(
        [
            call(email_configuration),
            call(ya_email_configuration),
            call(sender.default_configuration),
        ]
    )


def test_uses_first_configuration_if_it_is_not_raises(owl, mocker, configurations, email_configuration, ya_email_configuration):
    configurations.return_value = [email_configuration, ya_email_configuration]
    sender = owl()
    inner_send = mocker.patch.object(sender, "send")
    inner_send.side_effect = [None, TemplateNotFoundError(), TemplateNotFoundError()]

    sender()

    inner_send.assert_called_once_with(email_configuration)


def test_uses_default_configuration_if_there_are_no_configurations(owl, mocker, configurations):
    configurations.return_value = []
    sender = owl()
    inner_send = mocker.patch.object(sender, "send")

    sender()

    inner_send.assert_called_once_with(sender.default_configuration)


def test_doesnt_resend_with_different_error_code(owl, mocked_send):
    mocked_send.side_effect = make_exception(
        data={"ErrorCode": 1102, "Message": "The Template's 'Alias' associated with this request is not valid or was not found."},
        status_code=422,
    )

    with pytest.raises(AnymailRequestsAPIError):
        owl()()

    assert mocked_send.call_count == 1
