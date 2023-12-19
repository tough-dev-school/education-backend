import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def course(factory):
    return factory.course(
        price=0,
        confirmation_success_url="https://well.done",
    )


@pytest.fixture
def order(factory, course, mocker):
    mocker.patch("apps.orders.services.order_shipper.OrderShipper.write_success_admin_log")

    return factory.order(item=course, price=0)


@pytest.fixture(autouse=True)
def ship(mocker):
    return mocker.patch("apps.products.models.Course.ship")
