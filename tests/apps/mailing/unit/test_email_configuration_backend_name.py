import pytest

from apps.mailing.models import EmailConfiguration

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def _settings(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.dummy.EmailBackend"


@pytest.fixture
def email_configuration(mixer):
    return mixer.blend("mailing.EmailConfiguration")


@pytest.mark.parametrize(
    ("backend", "expected"),
    [
        (EmailConfiguration.BACKEND.UNSET, "django.core.mail.backends.dummy.EmailBackend"),
        (EmailConfiguration.BACKEND.POSTMARK, "anymail.backends.postmark.EmailBackend"),
    ],
)
def test(email_configuration, backend, expected):
    email_configuration.backend = backend
    email_configuration.save()

    email_configuration.refresh_from_db()
    assert email_configuration.backend_name == expected
