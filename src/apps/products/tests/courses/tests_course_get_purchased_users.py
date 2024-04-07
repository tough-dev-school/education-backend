import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def order(factory, course, user):
    order = factory.order(user=user, item=course, is_paid=True)

    return order


@pytest.fixture
def another_order(factory, user):
    order = factory.order(user=user, is_paid=True)

    return order


@pytest.mark.usefixtures("user")
def test_nothing(course) -> None:
    assert len(course.get_purchased_users()) == 0


@pytest.mark.usefixtures("order")
def test_one_user(course, user) -> None:
    assert user in course.get_purchased_users()


def test_single_user_in_two_orders(course, order, another_order) -> None:
    another_order.update(course=order.course)

    assert len(course.get_purchased_users()) == 1


def test_non_purchased(course, order) -> None:
    order.refund()

    assert len(course.get_purchased_users()) == 0


@pytest.mark.usefixtures("another_order")
def test_another_order(course) -> None:
    assert len(course.get_purchased_users()) == 0
