import pytest

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def _enable_amocrm(settings):
    settings.AMOCRM_BASE_URL = "https://test.amocrm.ru"
    settings.AMOCRM_REDIRECT_URL = "https://test-education.ru"
    settings.AMOCRM_INTEGRATION_ID = "4815162342"
    settings.AMOCRM_CLIENT_SECRET = "top-secret-007"
    settings.AMOCRM_AUTHORIZATION_CODE = "1337yep"


@pytest.fixture
def update_amocrm_order(mocker):
    return mocker.patch("apps.amocrm.tasks.AmoCRMOrderPusher.act")


@pytest.fixture
def update_amocrm_user(mocker):
    return mocker.patch("apps.amocrm.tasks.AmoCRMUserPusher.act")


@pytest.fixture(autouse=True)
def update_dashamail(mocker):
    return mocker.patch("apps.dashamail.tasks.DashamailSubscriber.subscribe")


@pytest.fixture(autouse=True)
def update_dashamail_directcrm(mocker):
    return mocker.patch("apps.dashamail.tasks.directcrm_events.OrderPaid.send")


@pytest.mark.usefixtures("_enable_amocrm")
def test_amocrm_is_updated(order, update_amocrm_order, update_amocrm_user):
    order.set_paid()

    update_amocrm_order.assert_called_once()
    update_amocrm_user.assert_called_once()


@pytest.mark.user_tags_rebuild()
def test_tags_are_rebuilt(order):
    assert "any-purchase" not in order.user.tags

    order.set_paid()
    order.user.refresh_from_db()

    assert "any-purchase" in order.user.tags


@pytest.mark.dashamail()
def test_dashamail_is_updated(order, update_dashamail):
    order.set_paid()

    update_dashamail.assert_called_once()


@pytest.mark.dashamail()
def test_dashamail_directm_is_updated(order, update_dashamail_directcrm):
    order.set_paid()

    update_dashamail_directcrm.assert_called_once()
