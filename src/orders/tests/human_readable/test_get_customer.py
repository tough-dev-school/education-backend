import pytest

from orders import human_readable

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def user(mixer):
    return mixer.blend(
        "users.User",
        first_name="Иван",
        last_name="Хрюнов",
        email="khrunov@gmail.com",
    )


@pytest.fixture
def order(order, user):
    order.setattr_and_save("user", user)
    return order


def test_include_first_name_last_name_if_name_and_email_are_short_enough(order):
    got = human_readable.get_order_customer(order)

    assert got == 'Иван Хрюнов &lt;<a href="mailto:khrunov@gmail.com">khrunov@gmail.com</a>&gt;'


def test_exclude_last_name_from_template_if_name_and_email_is_middle_sized(order):
    order.user.email = "ivan.khrunov@gmail.com"

    got = human_readable.get_order_customer(order)

    assert got == 'Иван &lt;<a href="mailto:ivan.khrunov@gmail.com">ivan.khrunov@gmail.com</a>&gt;'


def test_contains_email_only_if_name_and_email_is_to_long(order):
    order.user.email = "khrunov-has-very-long-email-that-exceeds-limits@gmail.com"

    got = human_readable.get_order_customer(order)

    assert got == '<a href="mailto:khrunov-has-very-long-email-that-exceeds-limits@gmail.com">khrunov-has-very-long-email-that-exceeds-limits@gmail.com</a>'
