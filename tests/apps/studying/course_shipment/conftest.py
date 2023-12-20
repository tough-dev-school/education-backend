from functools import partial
import pytest

from apps.studying.shipment import CourseShipment

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def course(factory):
    return factory.course(
        name="Кройка и шитьё",
        name_genitive="Кройки и шитья",
        slug="sewing",
    )


@pytest.fixture
def order(factory, course):
    return factory.order(item=course)


@pytest.fixture
def shipment(user, course, order):
    return partial(CourseShipment, user=user, product=course, order=order)
