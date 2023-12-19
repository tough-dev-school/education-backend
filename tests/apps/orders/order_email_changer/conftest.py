import pytest

from apps.orders.services import OrderEmailChanger

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def email_changer():
    return OrderEmailChanger


@pytest.fixture
def user(mixer):
    return mixer.blend("users.User", first_name="Kamaz", last_name="Otkhodov", email="kamaz@gmail.com")


@pytest.fixture
def nameless_user(mixer):
    return mixer.blend("users.User", first_name="", last_name="")


@pytest.fixture
def ship(mocker):
    return mocker.patch("apps.studying.shipment_factory.ship")


@pytest.fixture
def unship(mocker):
    return mocker.patch("apps.studying.shipment_factory.unship")


@pytest.fixture
def order(factory, mocker, nameless_user, course):
    mocker.patch("apps.orders.services.order_shipper.OrderShipper.write_success_admin_log")

    return factory.order(user=nameless_user, item=course)


@pytest.fixture(autouse=True)
def subscribe(mocker):
    return mocker.patch("apps.dashamail.tasks.update_subscription.delay")
