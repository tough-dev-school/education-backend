from datetime import datetime
from datetime import timedelta
from datetime import timezone
import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time("2032-12-01 15:30+05:00"),
]


@pytest.fixture
def mock_update_user_chain(mocker):
    return mocker.patch("orders.services.order_unpaid_setter.chain")


@pytest.fixture
def order(order):
    order.set_paid()

    return order


def test_update_user_tags(order, rebuild_tags):
    order.user.email = ""
    order.user.save()

    order.set_not_paid()

    rebuild_tags.assert_called_once_with(student_id=order.user.id, subscribe=False)


def test_call_update_user_celery_chain_with_subscription(
    order, mock_update_user_chain, mock_rebuild_tags, mock_push_customer, mock_return_order_in_amocrm, settings
):
    settings.AMOCRM_BASE_URL = "https://amo.amo.amo"

    order.set_not_paid()

    mock_update_user_chain.assert_called_once_with(
        mock_rebuild_tags(student_id=order.user.id, subscribe=True),
        mock_push_customer(user_id=order.user.id),
        mock_return_order_in_amocrm(order_id=order.id),
    )


def test_removes_study_record(order):
    order.set_not_paid()
    order.refresh_from_db()

    assert order.paid is None
    assert order.shipped is None
    assert not hasattr(order, "study"), "Study record should be deleted at this point"


def test_unships(order, unship):
    order.set_not_paid()

    unship.assert_called_once_with(order=order)


def test_not_unships_if_order_was_not_paid(order, unship):
    order.setattr_and_save("paid", None)

    order.set_not_paid()

    unship.assert_not_called()


def test_empty_item_does_not_break_things(order, unship):
    order.setattr_and_save("course", None)

    order.set_not_paid()

    unship.assert_not_called()


def test_sets_unpaid_date(order):
    order.set_not_paid()

    order.refresh_from_db()

    assert order.unpaid == datetime(2032, 12, 1, 15, 30, tzinfo=timezone(timedelta(hours=5)))


def test_does_not_set_unpaid_date_if_order_was_not_paid(order):
    order.setattr_and_save("paid", None)

    order.refresh_from_db()

    assert order.unpaid is None
