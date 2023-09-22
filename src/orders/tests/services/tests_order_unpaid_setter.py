from datetime import datetime
from datetime import timezone
import pytest

from orders.services import OrderUnpaidSetter

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def _enable_amocrm(settings):
    settings.AMOCRM_BASE_URL = "https://amo.amo.amo"


@pytest.fixture
def mock_rebuild_tags(mocker):
    return mocker.patch("users.tasks.rebuild_tags.delay")


@pytest.fixture
def order(factory, user, course):
    order = factory.order(user=user, item=course, price=9999)

    order.ship()
    order.setattr_and_save("paid", datetime.fromisoformat("2022-12-10 09:23Z"))  # set manually to skip side effects
    return order


@pytest.fixture
def set_unpaid(order):
    return lambda order=order: OrderUnpaidSetter(order=order)()


def test_update_user_tags(order, mock_rebuild_tags, set_unpaid):
    order.user.email = ""
    order.user.save()

    set_unpaid()

    mock_rebuild_tags.assert_called_once_with(student_id=order.user.id, subscribe=False)


@pytest.mark.usefixtures("_enable_amocrm")
def test_call_update_user_celery_chain_with_subscription(order, set_unpaid, mocker):
    mock_celery_chain = mocker.patch("orders.services.order_unpaid_setter.chain")
    mock_first_rebuild_tags = mocker.patch("users.tasks.rebuild_tags.si")
    mock_second_push_customer = mocker.patch("amocrm.tasks.push_user.si")
    mock_third_return_order_in_amocrm = mocker.patch("amocrm.tasks.return_order.si")

    set_unpaid()

    mock_celery_chain.assert_called_once_with(
        mock_first_rebuild_tags(student_id=order.user.id, subscribe=True),
        mock_second_push_customer(user_id=order.user.id),
        mock_third_return_order_in_amocrm(order_id=order.id),
    )


def test_removes_study_record(order, set_unpaid):
    set_unpaid()

    order.refresh_from_db()
    assert order.paid is None
    assert order.shipped is None
    assert not hasattr(order, "study"), "Study record should be deleted at this point"


def test_unships(order, set_unpaid, mock_item_unshipping):
    set_unpaid()

    mock_item_unshipping.assert_called_once_with(order=order)


def test_not_unships_if_order_was_not_paid(order, set_unpaid, mock_item_unshipping):
    order.setattr_and_save("paid", None)

    set_unpaid(order=order)

    mock_item_unshipping.assert_not_called()


def test_empty_item_does_not_break_things(order, set_unpaid, mock_item_unshipping):
    order.setattr_and_save("course", None)

    set_unpaid(order=order)

    mock_item_unshipping.assert_not_called()


@pytest.mark.freeze_time("2032-12-01 15:30Z")
def test_sets_unpaid_date(order, set_unpaid):
    set_unpaid()

    order.refresh_from_db()
    assert order.unpaid == datetime(2032, 12, 1, 15, 30, tzinfo=timezone.utc)


def test_does_not_set_unpaid_date_if_order_was_not_paid(order, set_unpaid):
    order.setattr_and_save("paid", None)

    set_unpaid(order=order)

    order.refresh_from_db()
    assert order.unpaid is None
