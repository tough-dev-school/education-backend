import pytest

from amocrm.models import AmoCRMOrderTransaction
from amocrm.services.orders.order_transaction_deleter import AmoCRMOrderTransactionDeleter
from amocrm.services.orders.order_transaction_deleter import AmoCRMOrderTransactionDeleterException

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def mock_delete_transaction(mocker):
    return mocker.patch("amocrm.client.AmoCRMClient.delete_transaction", return_value=None)


@pytest.fixture
def transaction_deleter():
    return lambda order: AmoCRMOrderTransactionDeleter(order=order)()


@pytest.fixture
def order(factory, order):
    factory.amocrm_order_transaction(order=order, amocrm_id=876)
    order.set_not_paid()
    return order


def test_deletes_amocrm_order_transaction(transaction_deleter, order):
    transaction_deleter(order)

    assert AmoCRMOrderTransaction.objects.all().count() == 0


def test_deletes_correct_call(transaction_deleter, order, mock_delete_transaction):
    transaction_deleter(order)

    mock_delete_transaction.assert_called_once_with(
        transaction_id=876,
    )


def test_fails_if_doesnt_exist(transaction_deleter, order):
    order.amocrm_transaction.delete()
    order.refresh_from_db()

    with pytest.raises(AmoCRMOrderTransactionDeleterException, match="Transaction doesnt exist"):
        transaction_deleter(order)


def test_fails_if_order_is_not_unpaid(transaction_deleter, order):
    order.unpaid = None
    order.save()

    with pytest.raises(AmoCRMOrderTransactionDeleterException, match="Order must be unpaid"):
        transaction_deleter(order)
