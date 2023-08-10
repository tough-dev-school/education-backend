import pytest

from amocrm.models import AmoCRMOrderTransaction
from amocrm.services.orders.order_transaction_creator import AmoCRMOrderTransactionCreator
from amocrm.services.orders.order_transaction_creator import AmoCRMOrderTransactionCreatorException
from amocrm.types import AmoCRMTransactionElement
from amocrm.types import AmoCRMTransactionElementMetadata

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def _mock_fields_id(mocker):
    mocker.patch("amocrm.services.orders.order_transaction_creator.get_catalog_id", return_value=777)


@pytest.fixture(autouse=True)
def mock_create_transaction(mocker):
    return mocker.patch("amocrm.client.AmoCRMClient.create_customer_transaction", return_value=481516)


@pytest.fixture
def transaction_creator():
    return lambda order: AmoCRMOrderTransactionCreator(order=order)()


def test_creates_amocrm_order_transaction(transaction_creator, order):
    got = transaction_creator(order)

    amocrm_transaction = AmoCRMOrderTransaction.objects.get()
    assert got == amocrm_transaction.amocrm_id
    assert amocrm_transaction.order == order
    assert amocrm_transaction.amocrm_id == 481516


def test_creates_correct_call(transaction_creator, order, mock_create_transaction):
    transaction_creator(order)

    mock_create_transaction.assert_called_once_with(
        customer_id=order.user.amocrm_user.amocrm_id,
        price=order.price,
        order_slug=order.slug,
        purchased_product=AmoCRMTransactionElement(
            id=order.course.amocrm_course.amocrm_id,
            metadata=AmoCRMTransactionElementMetadata(
                catalog_id=777,
                quantity=1,
            ),
        ),
    )


def test_fails_if_already_exist(transaction_creator, order, factory):
    factory.amocrm_order_transaction(order=order)

    with pytest.raises(AmoCRMOrderTransactionCreatorException, match="Transaction already exist"):
        transaction_creator(order)


def test_fails_if_no_course(transaction_creator, order):
    order.setattr_and_save("course", None)

    with pytest.raises(AmoCRMOrderTransactionCreatorException, match="Order doesn't have a course"):
        transaction_creator(order)


def test_fails_if_no_amocrm_course(transaction_creator, order):
    order.course.amocrm_course.delete()
    order.refresh_from_db()

    with pytest.raises(AmoCRMOrderTransactionCreatorException, match="Course doesn't exist in AmoCRM"):
        transaction_creator(order)


def test_fails_if_no_amocrm_customer(transaction_creator, order):
    order.user.amocrm_user.delete()
    order.refresh_from_db()

    with pytest.raises(AmoCRMOrderTransactionCreatorException, match="AmoCRM customer for order's user doesn't exist"):
        transaction_creator(order)
