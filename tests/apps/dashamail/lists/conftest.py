import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def _mock_subscription_updater() -> None:  # override global mock to test dashamail
    return


@pytest.fixture(autouse=True)
def _set_dashamail_credentials(settings) -> None:
    settings.DASHAMAIL_API_KEY = "apikey"
    settings.DASHAMAIL_LIST_ID = "1"


@pytest.fixture
def user(mixer):
    return mixer.blend(
        "users.User",
        email="test@e.mail",
        first_name="Rulon",
        last_name="Oboev",
        tags=["popug-3-self__purchased", "any-purchase"],
    )
