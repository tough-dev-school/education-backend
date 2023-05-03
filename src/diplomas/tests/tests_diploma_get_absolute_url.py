import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def _set_frontend_url(settings):
    settings.DIPLOMA_FRONTEND_URL = "https://certificates.borshev.com/"


@pytest.fixture
def diploma(factory):
    return factory.diploma(slug="secre7")


def test(diploma):
    assert diploma.get_absolute_url() == "https://certificates.borshev.com/secre7/"
