import pytest

from _decimal import Decimal

from amocrm.services.orders.order_pusher import AmoCRMOrderPusher
from amocrm.services.orders.order_pusher import AmoCRMOrderPusherException

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def mock_push_existing_order_to_amocrm(mocker):
    return mocker.patch("amocrm.tasks.push_existing_order_to_amocrm.delay")


@pytest.fixture
def mock_create_amocrm_lead(mocker):
    return mocker.patch("amocrm.tasks.create_amocrm_lead.delay")


@pytest.fixture
def mock_update_amocrm_lead(mocker):
    return mocker.patch("amocrm.tasks.update_amocrm_lead.delay")


@pytest.fixture
def paid_order_without_lead(user, course, factory):
    return factory.order(user=user, course=course, is_paid=True, author=user)


@pytest.fixture
def amocrm_lead(factory):
    return factory.amocrm_order_lead()


@pytest.fixture
def paid_order_with_lead(user, course, factory, amocrm_lead):
    return factory.order(user=user, course=course, is_paid=True, author=user, amocrm_lead=amocrm_lead)


@pytest.fixture
def not_paid_order_without_lead(factory, user, course):
    return factory.order(user=user, course=course, is_paid=False, author=user)


@pytest.fixture
def not_paid_order_with_lead(factory, user, course, amocrm_lead):
    return factory.order(user=user, course=course, is_paid=False, author=user, amocrm_lead=amocrm_lead)


@pytest.fixture
def returned_order_with_lead(factory, user, course, amocrm_lead):
    order = factory.order(user=user, course=course, is_paid=True, author=user, amocrm_lead=amocrm_lead)
    order.set_not_paid()
    return order


@pytest.fixture
def order_pusher():
    return lambda order: AmoCRMOrderPusher(order=order)()


def test_call_update_with_lead_not_paid(order_pusher, not_paid_order_with_lead, mock_update_amocrm_lead):
    order_pusher(order=not_paid_order_with_lead)

    mock_update_amocrm_lead.assert_called_once_with(order_id=not_paid_order_with_lead.id)


def test_call_create_without_lead_not_paid(order_pusher, not_paid_order_without_lead, mock_create_amocrm_lead):
    order_pusher(order=not_paid_order_without_lead)

    mock_create_amocrm_lead.assert_called_once_with(order_id=not_paid_order_without_lead.id)


def test_call_update_with_lead_paid(order_pusher, paid_order_with_lead, mock_push_existing_order_to_amocrm):
    order_pusher(order=paid_order_with_lead)

    mock_push_existing_order_to_amocrm.assert_called_once_with(order_id=paid_order_with_lead.id)


def test_call_update_with_lead_returned(order_pusher, returned_order_with_lead, mock_push_existing_order_to_amocrm):
    order_pusher(order=returned_order_with_lead)

    mock_push_existing_order_to_amocrm.assert_called_once_with(order_id=returned_order_with_lead.id)


def test_new_not_paid_order_linked_to_existing_lead_calls_update(
    order_pusher, not_paid_order_without_lead, not_paid_order_with_lead, mock_update_amocrm_lead, mock_create_amocrm_lead, amocrm_lead
):
    order_pusher(order=not_paid_order_without_lead)

    not_paid_order_without_lead.amocrm_lead.refresh_from_db()
    assert not_paid_order_without_lead.amocrm_lead == amocrm_lead
    mock_update_amocrm_lead.assert_called_once_with(order_id=not_paid_order_without_lead.id)
    mock_create_amocrm_lead.assert_not_called()


def test_new_paid_order_linked_to_existing_lead_calls_update(
    order_pusher,
    paid_order_without_lead,
    not_paid_order_with_lead,
    mock_push_existing_order_to_amocrm,
    mock_update_amocrm_lead,
    mock_create_amocrm_lead,
    amocrm_lead,
):
    order_pusher(order=paid_order_without_lead)

    paid_order_without_lead.amocrm_lead.refresh_from_db()
    assert paid_order_without_lead.amocrm_lead == amocrm_lead
    mock_push_existing_order_to_amocrm.assert_called_once_with(order_id=paid_order_without_lead.id)


def test_new_order_linked_to_existing_lead_from_returned_order_calls_update(
    order_pusher,
    paid_order_without_lead,
    returned_order_with_lead,
    mock_push_existing_order_to_amocrm,
    mock_update_amocrm_lead,
    mock_create_amocrm_lead,
    amocrm_lead,
):
    order_pusher(order=paid_order_without_lead)

    paid_order_without_lead.amocrm_lead.refresh_from_db()
    mock_push_existing_order_to_amocrm.assert_called_once_with(order_id=paid_order_without_lead.id)
    assert paid_order_without_lead.amocrm_lead == amocrm_lead


def test_not_push_if_author_not_equal_to_user(
    order_pusher,
    not_paid_order_without_lead,
    mock_push_existing_order_to_amocrm,
    another_user,
    mock_update_amocrm_lead,
    mock_create_amocrm_lead,
):
    not_paid_order_without_lead.author = another_user
    not_paid_order_without_lead.save()

    order_pusher(order=not_paid_order_without_lead)

    mock_push_existing_order_to_amocrm.assert_not_called()
    mock_update_amocrm_lead.assert_not_called()
    mock_create_amocrm_lead.assert_not_called()


def test_not_push_if_free_order(
    order_pusher,
    not_paid_order_without_lead,
    mock_push_existing_order_to_amocrm,
    mock_update_amocrm_lead,
    mock_create_amocrm_lead,
):
    not_paid_order_without_lead.price = Decimal(0)
    not_paid_order_without_lead.save()

    order_pusher(order=not_paid_order_without_lead)

    mock_push_existing_order_to_amocrm.assert_not_called()
    mock_update_amocrm_lead.assert_not_called()
    mock_create_amocrm_lead.assert_not_called()


def test_not_push_if_there_is_already_paid_order(
    order_pusher,
    not_paid_order_without_lead,
    paid_order_with_lead,
    mock_push_existing_order_to_amocrm,
    mock_update_amocrm_lead,
    mock_create_amocrm_lead,
):
    order_pusher(order=not_paid_order_without_lead)

    mock_push_existing_order_to_amocrm.assert_not_called()
    mock_update_amocrm_lead.assert_not_called()
    mock_create_amocrm_lead.assert_not_called()


def test_fails_if_many_lead_for_same_course_and_user(order_pusher, factory, not_paid_order_without_lead):
    leads = factory.cycle(2).amocrm_order_lead()
    for lead in leads:
        factory.order(user=not_paid_order_without_lead.user, course=not_paid_order_without_lead.course, is_paid=False, amocrm_lead=lead)

    with pytest.raises(AmoCRMOrderPusherException, match="There are duplicates leads for such order with same course and user"):
        order_pusher(not_paid_order_without_lead)


def test_fail_create_paid_without_lead(order_pusher, paid_order_without_lead):
    with pytest.raises(AmoCRMOrderPusherException, match="Cannot push paid or unpaid order without existing lead"):
        order_pusher(order=paid_order_without_lead)
