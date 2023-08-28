import pytest


@pytest.fixture(autouse=True)
def _settings_amocrm(settings):
    settings.AMOCRM_BASE_URL = "https://test.amocrm.ru"
    settings.AMOCRM_REDIRECT_URL = "https://test-education.ru"
    settings.AMOCRM_INTEGRATION_ID = "4815162342"
    settings.AMOCRM_CLIENT_SECRET = "top-secret-007"
    settings.AMOCRM_AUTHORIZATION_CODE = "1337yep"


@pytest.fixture
def amocrm_user(factory, user):
    return factory.amocrm_user(user=user)


@pytest.fixture
def amocrm_course(factory, course):
    return factory.amocrm_course(course=course)


@pytest.fixture(autouse=True)
def _mock_tasks_with_paid_setter(mocker):
    mocker.patch("orders.services.order_paid_setter.OrderPaidSetter.after_shipment", return_value=None)
    mocker.patch("orders.services.order_unpaid_setter.OrderUnpaidSetter.after_unshipment", return_value=None)
    mocker.patch("studying.shipment_factory.unship", return_value=None)
