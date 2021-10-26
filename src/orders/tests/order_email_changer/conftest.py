import pytest

from orders.services import OrderEmailChanger

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def email_changer():
    return OrderEmailChanger


@pytest.fixture
def user(mixer):
    return mixer.blend('users.User', first_name='Kamaz', last_name='Otkhodov', email='kamaz@gmail.com')


@pytest.fixture
def ship(mocker):
    return mocker.patch('studying.shipment_factory.ship')


@pytest.fixture
def unship(mocker):
    return mocker.patch('studying.shipment_factory.unship')


@pytest.fixture
def order(factory, course):
    return factory.order(course=course)


@pytest.fixture
def paid_order(factory, course):
    return factory.order(course=course, is_paid=True)
