import pytest
from functools import partial

from studying.shipment import CourseShipment

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def course(mixer):
    return mixer.blend(
        'products.Course',
        name='Кройка и шитьё',
        name_genitive='Кройки и шитья',
        slug='sewing',
    )


@pytest.fixture
def order(factory, course):
    return factory.order(item=course)


@pytest.fixture
def shipment(user, course, order):
    return partial(CourseShipment, user=user, product=course, order=order)


@pytest.fixture(autouse=True)
def invite_to_zoomus(mocker):
    return mocker.patch('app.tasks.invite_to_zoomus.delay')


@pytest.fixture
def giver(mixer):
    return mixer.blend('users.User', first_name='Робин', last_name='Бетмен')


@pytest.fixture
def gifted_order(factory, course, giver):
    return factory.order(
        item=course,
        giver=giver,
        desired_shipment_date='2025-01-05',
        gift_message='Гори в аду!',
    )
