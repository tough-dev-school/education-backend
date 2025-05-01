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
    settings.PER_COURSE_EMAIL_CONFIGURATION = True


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
def configurations(email_configration, mocker):
    return mocker.patch("apps.mailing.owl.get_configurations", return_value=EmailConfiguration.objects.filter(pk=email_configration.pk))


@pytest.fixture
def owl(owl):
    return owl()


@pytest.fixture
def test_backend(mocker):
    return mocker.patch(f"{TEST_BACKEND}.__init__", return_value=None)


def test_defaults(owl):
    message = owl.get_message(owl.default_configuration)

    assert message.from_email == DEFAULT_FROM_EMAIL
    assert message.reply_to == [DEFAULT_REPLY_TO]


@pytest.mark.usefixtures("configurations")
def test_custom(owl):
    message = owl.get_message(owl.configurations[0])

    assert message.from_email == TEST_FROM_EMAIL
    assert message.reply_to == [TEST_REPLY_TO]


@pytest.mark.usefixtures("configurations")
def test_custom_configuration_is_applied(owl, email_configration, test_backend):
    email_configration.backend_options = {"test": "__mocked"}
    email_configration.save()

    owl.get_connection(owl.configurations[0])  # call the connection property

    test_backend.assert_called_once_with(fail_silently=False, test="__mocked")
