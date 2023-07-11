import pytest

from users.tags.pipeline import apply_tags

pytestmark = [pytest.mark.django_db]


@pytest.mark.usefixtures("non_paid_order")
def test_order_started(user):
    apply_tags(user)

    assert "any-purchase" not in user.tags


def test_free_order_purchased(user, paid_order):
    paid_order.price = 0
    paid_order.save()

    apply_tags(user)

    assert "any-purchase" not in user.tags


@pytest.mark.usefixtures("paid_order")
def test_order_purchased(user):
    apply_tags(user)

    assert "any-purchase" in user.tags
