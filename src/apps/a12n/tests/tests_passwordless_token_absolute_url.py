import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def _freeze_absolute_url(settings):
    settings.FRONTEND_URL = "https://frontend/lms/"


def test(mixer):
    token = mixer.blend("a12n.PasswordlessAuthToken", token="3149798e-c219-47f5-921f-8ae9a75b709b")

    assert token.get_absolute_url() == "https://frontend/lms/auth/passwordless/3149798e-c219-47f5-921f-8ae9a75b709b/"
