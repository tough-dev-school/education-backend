import pytest


@pytest.fixture
def user(mixer):
    return mixer.blend('users.User', email="big@guy.com")

@pytest.fixture
def order(factory, course, mocker, user):
    mocker.patch("apps.orders.services.order_shipper.OrderShipper.write_success_admin_log")

    return factory.order(item=course, user=user, is_paid=False, price='100500.65')

@pytest.fixture
def course(factory):
    return factory.course(
        slug="aa-5-full",
        name="Как стать таким же умным как Антон Давыдов",
    )
