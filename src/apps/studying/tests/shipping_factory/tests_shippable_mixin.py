import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def ship(mocker):
    return mocker.patch("apps.studying.shipment.CourseShipment.ship")


@pytest.fixture
def order(factory):
    return factory.order()


def test_course(course, ship, user, order):
    course.ship(to=user, order=order)

    ship.assert_called_once()
