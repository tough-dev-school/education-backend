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
def nameless_user(mixer):
    return mixer.blend('users.User', first_name='', last_name='')


@pytest.fixture
def ship(mocker):
    return mocker.patch('studying.shipment_factory.ship')


@pytest.fixture
def unship(mocker):
    return mocker.patch('studying.shipment_factory.unship')


@pytest.fixture
def order(factory, nameless_user, course):
    return factory.order(user=nameless_user, course=course)
