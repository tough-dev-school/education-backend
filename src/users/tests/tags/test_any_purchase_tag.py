import pytest

from users.tags import AnyPurchaseTag

pytestmark = [pytest.mark.django_db]

tag_name = AnyPurchaseTag.tag_name


@pytest.fixture
def tag_mechanism():
    return lambda student: AnyPurchaseTag(student)


@pytest.mark.usefixtures("paid_order", "unpaid_order")
def test_return_tag_if_has_paid_order(tag_mechanism, user):
    got = tag_mechanism(user)()

    assert got == [tag_name]


@pytest.mark.usefixtures("unpaid_order")
def test_return_empty_list_if_no_paid_orders(tag_mechanism, user):
    got = tag_mechanism(user)()

    assert got == []


def test_return_empty_list_if_no_orders(tag_mechanism, user):
    got = tag_mechanism(user)()

    assert got == []
