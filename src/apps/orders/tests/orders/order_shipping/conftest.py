import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def user(mixer):
    return mixer.blend("users.User", first_name="Kamaz", last_name="Otkhodov", email="kamaz@gmail.com")


@pytest.fixture
def ship(mocker):
    return mocker.patch("apps.studying.shipment_factory.ship")


@pytest.fixture
def course(factory):
    return factory.course(
        name_genitive="курсов катанья и мытья",
        name="Запись курсов катанья и мытья",
        full_name="Полная запись курса катанья и мытья",
        group=factory.group(name="testgroup"),
    )


@pytest.fixture
def order(factory, course, user):
    return factory.order(user=user, price=1500, item=course)
