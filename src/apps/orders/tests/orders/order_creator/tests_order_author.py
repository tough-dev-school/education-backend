import pytest

pytestmark = [pytest.mark.django_db]


def test_default_author_is_the_order_user(create, user, course):
    order = create(user=user, item=course)

    order.refresh_from_db()

    assert order.author == user


@pytest.mark.usefixtures("_set_current_user")
def test_current_user_if_specified(create, user, another_user, course):
    order = create(user=another_user, item=course)

    order.refresh_from_db()

    assert order.author == user, "User is set from the current user"


def test_manualy_specified_author(create, user, another_user, course):
    order = create(user=user, item=course, author=another_user)

    order.refresh_from_db()

    assert order.author == another_user, "Manuly specified author"
