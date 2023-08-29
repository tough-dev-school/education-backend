import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def mock_rebuild_tags(mocker):
    return mocker.patch("users.tasks.rebuild_tags.si")


@pytest.fixture
def mock_push_customer(mocker):
    return mocker.patch("amocrm.tasks.push_user.si")


@pytest.fixture
def mock_push_order(mocker):
    return mocker.patch("amocrm.tasks.push_order.si")


@pytest.fixture
def mock_return_order_in_amocrm(mocker):
    return mocker.patch("amocrm.tasks.return_order.si")


@pytest.fixture(autouse=True)
def rebuild_tags(mocker):
    return mocker.patch("users.tasks.rebuild_tags.delay")


@pytest.fixture
def user(mixer):
    return mixer.blend("users.User", first_name="Kamaz", last_name="Otkhodov", email="kamaz@gmail.com")


@pytest.fixture
def ship(mocker):
    return mocker.patch("studying.shipment_factory.ship")


@pytest.fixture
def unship(mocker):
    return mocker.patch("studying.shipment_factory.unship")


@pytest.fixture
def course(factory):
    return factory.course(name_genitive="курсов катанья и мытья", name="Запись курсов катанья и мытья", full_name="Полная запись курса катанья и мытья")


@pytest.fixture
def order(factory, course, user):
    order = factory.order(user=user, price=1500)
    order.set_item(course)

    return order
