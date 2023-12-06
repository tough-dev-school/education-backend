import pytest

from apps.users.tags.pipeline import generate_tags

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.user_tags_rebuild,
]


@pytest.mark.usefixtures("non_paid_order")
def test_order_started(user):
    generate_tags(user)

    assert "any-purchase" not in user.tags


def test_free_order_purchased(user, paid_order):
    paid_order.update(price=0)

    generate_tags(user)

    assert "any-purchase" not in user.tags


@pytest.mark.usefixtures("paid_order")
def test_order_purchased(user):
    generate_tags(user)

    assert "any-purchase" in user.tags
