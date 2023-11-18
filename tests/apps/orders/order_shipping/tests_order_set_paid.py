from datetime import datetime
from datetime import timezone
import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time("2032-12-01 15:30Z"),
]


@pytest.fixture
def mock_update_user_chain(mocker):
    return mocker.patch("apps.orders.services.order_paid_setter.chain")


def test_works(order):
    assert order.paid is None

    order.set_paid()
    order.refresh_from_db()

    assert order.paid == datetime(2032, 12, 1, 15, 30, tzinfo=timezone.utc)
    assert order.study is not None


def test_ships(order, course, user, ship):
    order.set_paid()

    ship.assert_called_once_with(course, to=user, order=order)


def test_update_user_tags(order, rebuild_tags):
    order.user.update(email="")

    order.set_paid()

    rebuild_tags.assert_called_once_with(student_id=order.user.id, subscribe=False)


def test_call_update_user_celery_chain_with_subscription(order, mock_update_user_chain, mock_rebuild_tags, mock_push_customer, mock_push_order, settings):
    settings.AMOCRM_BASE_URL = "https://amo.amo.amo"

    order.set_paid()

    mock_update_user_chain.assert_called_once_with(
        mock_rebuild_tags(student_id=order.user.id, subscribe=True),
        mock_push_customer(user_id=order.user.id),
        mock_push_order(order_id=order.id),
    )


def test_call_update_user_celery_chain_without_subscription(order, mock_update_user_chain, mock_rebuild_tags, mock_push_customer, mock_push_order, settings):
    settings.AMOCRM_BASE_URL = "https://amo.amo.amo"
    order.user.update(email="")

    order.set_paid()

    mock_update_user_chain.assert_called_once_with(
        mock_rebuild_tags(student_id=order.user.id, subscribe=False),
        mock_push_customer(user_id=order.user.id),
        mock_push_order(order_id=order.id),
    )


def test_not_ships_if_order_is_already_paid(order, ship):
    order.update(paid=datetime(2032, 12, 1, 15, 30, tzinfo=timezone.utc))

    order.set_paid()

    ship.assert_not_called()


def test_shipment_date(order):
    order.set_paid()
    order.refresh_from_db()

    assert order.shipped == datetime(2032, 12, 1, 15, 30, tzinfo=timezone.utc)


def test_order_is_not_shipped_again_if_already_shipped(order, ship):
    order.update(shipped=datetime(2032, 12, 1, 15, 30, tzinfo=timezone.utc))

    order.set_paid()

    ship.assert_not_called()


def test_shipment_date_is_not_reset(order, ship):
    order.update(shipped=datetime(2000, 11, 12, 1, 13, tzinfo=timezone.utc))

    order.set_paid()
    order.refresh_from_db()

    assert order.shipped == datetime(2000, 11, 12, 1, 13, tzinfo=timezone.utc)


def test_unpaid_date_is_reset(order):
    order.update(unpaid=datetime(2032, 12, 1, 15, 13, tzinfo=timezone.utc))

    order.set_paid()
    order.refresh_from_db()

    assert order.unpaid is None


def test_unpaid_date_is_not_reset_when_order_is_not_paid(order):
    order.update(
        paid=datetime(2032, 12, 1, 12, 13, tzinfo=timezone.utc),
        unpaid=datetime(2032, 12, 1, 15, 13, tzinfo=timezone.utc),
    )

    order.set_paid()
    order.refresh_from_db()

    assert order.unpaid == datetime(2032, 12, 1, 15, 13, tzinfo=timezone.utc), "unpaid has not been changed"


def test_empty_item_does_not_break_things(order, ship):
    order.update(course=None)

    order.set_paid()

    ship.assert_not_called()
