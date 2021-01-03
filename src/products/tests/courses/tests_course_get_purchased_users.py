import pytest
from django.utils import timezone

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def course(mixer):
    return mixer.blend('products.Course')


@pytest.fixture
def order(mixer, course, user):
    return mixer.blend('orders.Order', user=user, course=course, paid=timezone.now())


@pytest.fixture
def another_order(mixer, user):
    return mixer.blend('orders.Order', user=user, paid=timezone.now())


@pytest.mark.usefixtures('user')
def test_nothing(course):
    assert len(course.get_purchased_users()) == 0


@pytest.mark.usefixtures('order')
def test_one_user(course, user):
    assert user in course.get_purchased_users()


def test_single_user_in_two_orders(course, order, another_order):
    another_order.setattr_and_save('course', order.course)

    assert len(course.get_purchased_users()) == 1


def test_two_users(course, order, user, another_order, another_user):
    another_order.update_from_kwargs(course=order.course, user=another_user)
    another_order.save()

    assert user in course.get_purchased_users()
    assert another_user in course.get_purchased_users()


def test_non_purchased(course, order):
    order.setattr_and_save('paid', None)

    assert len(course.get_purchased_users()) == 0


@pytest.mark.usefixtures('another_order')
def test_another_order(course):
    assert len(course.get_purchased_users()) == 0
