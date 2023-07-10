import pytest

from django.utils import timezone

from users.tags.mechanisms import AnyPurchaseTag
from users.tags.pipeline import apply_tags

pytestmark = [pytest.mark.django_db]

tag_name = AnyPurchaseTag.tag_name


@pytest.fixture
def paid_order(factory, user):
    return factory.order(user=user, paid=timezone.now(), unpaid=None, shipped=None)


@pytest.fixture
def unpaid_order(factory, user):
    return factory.order(user=user, unpaid=timezone.now(), paid=None, shipped=None)


@pytest.fixture
def mock_apply_tag(mocker):
    return mocker.patch("users.tags.mechanisms.AnyPurchaseTag.apply")


@pytest.mark.usefixtures("paid_order", "unpaid_order")
def test_set_if_has_paid_order_and_no_tag(user):
    apply_tags(user)

    assert tag_name in user.tags


@pytest.mark.usefixtures("paid_order", "unpaid_order")
def test_doesnt_set_if_already_has_tag(user, mock_apply_tag):
    user.tags = [tag_name]
    user.save()

    apply_tags(user)

    mock_apply_tag.assert_not_called()


@pytest.mark.usefixtures("unpaid_order")
def test_doesnt_set_if_no_paid_orders(user, mock_apply_tag):
    apply_tags(user)

    assert tag_name not in user.tags
    mock_apply_tag.assert_not_called()
