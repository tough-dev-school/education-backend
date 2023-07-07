import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def order(factory, course, user):
    order = factory.order(user=user, item=course)
    order.set_paid()

    return order


@pytest.fixture
def another_order(factory, user):
    order = factory.order(user=user)
    order.set_paid()

    return order


@pytest.mark.usefixtures("user")
def test_nothing(course):
    assert len(course.get_purchased_users()) == 0


@pytest.mark.usefixtures("order")
def test_one_user(course, user):
    assert user in course.get_purchased_users()


def test_single_user_in_two_orders(course, order, another_order):
    another_order.set_item(order.course)

    assert len(course.get_purchased_users()) == 1


def test_non_purchased(course, order):
    order.set_not_paid()

    assert len(course.get_purchased_users()) == 0


@pytest.mark.usefixtures("another_order")
def test_another_order(course):
    assert len(course.get_purchased_users()) == 0
