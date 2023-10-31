import pytest

from apps.mailing.models import EmailConfiguration

pytestmark = [pytest.mark.django_db]

DEFAULT_BACKEND = "django.core.mail.backends.dummy.EmailBackend"
TEST_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

DEFAULT_FROM_EMAIL = "Donald T <trump@employee.trumphotels.com>"
TEST_FROM_EMAIL = "Mark Z <zuckerberg@facebook-team.com>"

DEFAULT_REPLY_TO = "Secretary of Donald T <support@trumphotels.com"
TEST_REPLY_TO = "Mark Z Humanizm attorney <devnull@fb.com>"


@pytest.fixture(autouse=True)
def _settings(settings):
    settings.DEBUG = False
    settings.EMAIL_BACKEND = DEFAULT_BACKEND
    settings.DEFAULT_FROM_EMAIL = DEFAULT_FROM_EMAIL
    settings.DEFAULT_REPLY_TO = DEFAULT_REPLY_TO


@pytest.fixture
def email_configration(mixer):
    return mixer.blend(
        "mailing.EmailConfiguration",
        backend=TEST_BACKEND,
        from_email=TEST_FROM_EMAIL,
        reply_to=TEST_REPLY_TO,
        backend_options={},
    )


@pytest.fixture
def configuration(email_configration, mocker):
    return mocker.patch("apps.mailing.owl.get_configuration", return_value=email_configration)


@pytest.fixture
def owl(owl):
    return owl()


def test_defaults(owl):
    assert owl.backend_name == DEFAULT_BACKEND
    assert owl.msg.from_email == DEFAULT_FROM_EMAIL
    assert owl.msg.reply_to == [DEFAULT_REPLY_TO]


def test_custom(owl, configuration):
    assert owl.backend_name == TEST_BACKEND
    assert owl.msg.from_email == TEST_FROM_EMAIL
    assert owl.msg.reply_to == [TEST_REPLY_TO]


def test_default_backend_for_configuration_with_unset_backend(owl, configuration):
    configuration.return_value.backend = EmailConfiguration.BACKEND.UNSET

    assert owl.backend_name == DEFAULT_BACKEND


def test_backend_options_are_applyed(owl, configuration, mocker):
    configuration.return_value.backend_options = {"test": "__mocked"}

    backend_init = mocker.patch(f"{TEST_BACKEND}.__init__", return_value=None)

    owl.connection  # call the connection property

    backend_init.assert_called_once_with(fail_silently=False, test="__mocked")
