from _decimal import Decimal

import pytest

from apps.amocrm.models import AmoCRMOrderLead, AmoCRMOrderTransaction
from apps.amocrm.services.orders.order_pusher import AmoCRMOrderPusher, AmoCRMOrderPusherException

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def mock_create_transaction(mocker):
    mocker.patch("apps.amocrm.dto.transaction.AmoCRMTransactionDTO.create", return_value=22222)
    return mocker.patch("apps.amocrm.dto.transaction.AmoCRMTransactionDTO.__init__", return_value=None)


@pytest.fixture
def mock_create_lead(mocker):
    mocker.patch("apps.amocrm.dto.lead.AmoCRMLeadDTO.create", return_value=11111)
    return mocker.patch("apps.amocrm.dto.lead.AmoCRMLeadDTO.__init__", return_value=None)


@pytest.fixture
def mock_update_lead(mocker):
    return mocker.patch("apps.amocrm.dto.lead.AmoCRMLeadDTO.update")


@pytest.fixture
def mock_push_lead(mocker):
    return mocker.patch("apps.amocrm.services.orders.order_pusher.AmoCRMOrderPusher.push_lead")


@pytest.fixture
def mock_push_order(mocker):
    return mocker.patch("apps.amocrm.services.orders.order_pusher.AmoCRMOrderPusher.push_order")


@pytest.fixture
def not_paid_order_without_lead(factory, user, course):
    return factory.order(user=user, item=course, is_paid=False, author=user)


@pytest.fixture
def not_paid_order_with_lead(factory, user, course, amocrm_lead):
    return factory.order(user=user, item=course, is_paid=False, author=user, amocrm_lead=amocrm_lead)


@pytest.fixture
def returned_order_with_lead(factory, user, course, amocrm_lead):
    order = factory.order(user=user, item=course, is_paid=True, author=user, amocrm_lead=amocrm_lead)
    order.refund(order.price)
    return order


@pytest.mark.usefixtures("mock_create_lead")
def test_create_lead_if_no_lead_not_paid(not_paid_order_without_lead):
    """Поступил новый открытый заказ, аналогичной сделки в Амо еще нет - создается новая сделка в Амо"""
    AmoCRMOrderPusher(order=not_paid_order_without_lead)()

    not_paid_order_without_lead.refresh_from_db()
    assert not_paid_order_without_lead.amocrm_lead.amocrm_id == 11111


@pytest.mark.usefixtures("mock_create_transaction")
def test_create_order_if_paid(paid_order_with_lead, mock_update_lead):
    """Поступила оплата заказа - пушим весь заказ (обновляем Сделку и создаем Покупку)"""
    AmoCRMOrderPusher(order=paid_order_with_lead)()

    paid_order_with_lead.refresh_from_db()
    assert paid_order_with_lead.amocrm_transaction.amocrm_id == 22222
    mock_update_lead.assert_called_once_with(status="purchased")


@pytest.mark.usefixtures("mock_create_lead")
def test_created_lead_is_linked(not_paid_order_without_lead):
    """Созданная сделка должна быть прикреплена к заказу"""
    AmoCRMOrderPusher(order=not_paid_order_without_lead)()

    assert AmoCRMOrderLead.objects.get().order == not_paid_order_without_lead


@pytest.mark.usefixtures("mock_create_transaction", "mock_update_lead")
def test_created_transaction_is_linked(paid_order_with_lead):
    """Созданная транзакция должна быть прикреплена к заказу"""
    AmoCRMOrderPusher(order=paid_order_with_lead)()

    assert AmoCRMOrderTransaction.objects.get().order == paid_order_with_lead


@pytest.mark.usefixtures("mock_update_lead", "not_paid_order_with_lead")
def test_order_is_relinked(not_paid_order_without_lead, amocrm_lead):
    """Поступил новый открытый заказ, но аналогичная сделка уже есть в Амо - привязываем сделку к текущему заказу"""
    AmoCRMOrderPusher(order=not_paid_order_without_lead)()

    not_paid_order_without_lead.refresh_from_db()
    assert not_paid_order_without_lead.amocrm_lead == amocrm_lead


@pytest.mark.usefixtures("not_paid_order_with_lead")
def test_amocrm_lead_status_is_updated(not_paid_order_without_lead, mock_update_lead):
    """
    Поступил новый открытый заказ, но аналогичная сделка уже есть в Амо - привязываем сделку к текущему заказу и обновляем сделку в Амо,
    устанавливаем статус как "новое обращение", чтобы гарантированно вернуть сделку в "активное" состояние
    """
    AmoCRMOrderPusher(order=not_paid_order_without_lead)()

    mock_update_lead.assert_called_once_with(status="first_contact")


@pytest.mark.usefixtures("not_paid_order_with_lead", "mock_create_transaction")
def test_relink_and_create_order_if_paid(paid_order_without_lead, amocrm_lead, mock_update_lead):
    """Поступила оплата по заказу, но соответствующая сделка привязана к другому аналогичному заказу - привязываем сделку к текущему заказу и пушим в Амо"""
    AmoCRMOrderPusher(order=paid_order_without_lead)()

    paid_order_without_lead.refresh_from_db()
    assert paid_order_without_lead.amocrm_lead == amocrm_lead
    assert paid_order_without_lead.amocrm_transaction.amocrm_id == 22222
    mock_update_lead.assert_called_once_with(status="purchased")


@pytest.mark.usefixtures("returned_order_with_lead")
def test_relink_new_not_paid_order_from_returned(not_paid_order_without_lead, amocrm_lead, mock_update_lead):
    """
    Поступил новый открытый заказ, но сделка привязана к другому аналогичному возвращенному заказу -
    привязываем сделку к текущему заказу и обновляем в Амо
    """
    AmoCRMOrderPusher(order=not_paid_order_without_lead)()

    not_paid_order_without_lead.refresh_from_db()
    assert not_paid_order_without_lead.amocrm_lead == amocrm_lead
    mock_update_lead.assert_called_once()


def test_not_push_if_author_not_equal_to_user(not_paid_order_without_lead, another_user, mock_push_lead, mock_push_order):
    not_paid_order_without_lead.update(author=another_user)

    AmoCRMOrderPusher(order=not_paid_order_without_lead)()

    mock_push_lead.assert_not_called()
    mock_push_order.assert_not_called()


def test_not_push_if_free_order(not_paid_order_without_lead, mock_push_lead, mock_push_order):
    not_paid_order_without_lead.update(price=Decimal(0))

    AmoCRMOrderPusher(order=not_paid_order_without_lead)()

    mock_push_lead.assert_not_called()
    mock_push_order.assert_not_called()


@pytest.mark.usefixtures("paid_order_with_lead")
def test_not_push_if_there_is_already_paid_order(not_paid_order_without_lead, mock_push_lead, mock_push_order):
    AmoCRMOrderPusher(order=not_paid_order_without_lead)()

    mock_push_lead.assert_not_called()
    mock_push_order.assert_not_called()


def test_fail_create_paid_order_without_lead(paid_order_without_lead):
    with pytest.raises(AmoCRMOrderPusherException, match="Cannot push paid order without existing lead"):
        AmoCRMOrderPusher(order=paid_order_without_lead)()
