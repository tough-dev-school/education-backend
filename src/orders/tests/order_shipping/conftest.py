import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def user(mixer):
    return mixer.blend('users.User', first_name='Kamaz', last_name='Otkhodov', email='kamaz@gmail.com')


@pytest.fixture(autouse=True)
def ship(mocker):
    return mocker.patch('studying.factory.ship')


@pytest.fixture(autouse=True)
def unship(mocker):
    return mocker.patch('studying.factory.unship')


@pytest.fixture
def record(mixer):
    return mixer.blend('products.Record', course__name_genitive='курсов катанья и мытья', full_name='Полная запись курса катанья и мытья')


@pytest.fixture
def order(mixer, record, user):
    order = mixer.blend('orders.Order', user=user, price=1500)
    order.set_item(record)

    return order
