import pytest

from amocrm.services.orders.order_creator import AmoCRMOrderCreator
from amocrm.services.orders.order_creator import AmoCRMOrderCreatorException

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def _mock_b2c_fields_id(mocker):
    mocker.patch("amocrm.services.orders.order_creator.get_pipeline_id", return_value=777)
    mocker.patch("amocrm.services.orders.order_creator.get_b2c_pipeline_status_id", return_value=999)


@pytest.fixture
def mock_paid_status_id(mocker):
    return mocker.patch("amocrm.services.orders.order_creator.AmoCRMOrderCreator._paid_status_id", return_value=222)


@pytest.fixture
def mock_unpaid_status_id(mocker):
    return mocker.patch("amocrm.services.orders.order_creator.AmoCRMOrderCreator._unpaid_status_id", return_value=333)


@pytest.fixture
def mock_not_paid_or_unpaid(mocker):
    return mocker.patch("amocrm.services.orders.order_creator.AmoCRMOrderCreator._not_paid_or_unpaid_status_id", return_value=444)


@pytest.fixture(autouse=True)
def mock_update_lead(mocker):
    return mocker.patch("amocrm.client.AmoCRMClient.update_lead", return_value=481516)


@pytest.fixture
def order_creator():
    return lambda amocrm_lead: AmoCRMOrderCreator(amocrm_lead=amocrm_lead)()


def test_updates_amocrm_order_lead(order_creator, amocrm_lead):
    got = order_creator(amocrm_lead)

    assert got == 481516


def test_updates_correct_call_for_paid(order_creator, amocrm_lead, mock_update_lead, mock_paid_status_id):
    amocrm_lead.order.set_paid()

    order_creator(amocrm_lead)

    mock_update_lead.assert_called_once_with(
        lead_id=amocrm_lead.amocrm_id,
        status_id=mock_paid_status_id,
        pipeline_id=777,
        price=amocrm_lead.order.price,
        created_at=amocrm_lead.order.created,
    )


def test_updates_correct_call_for_unpaid(order_creator, amocrm_lead, mock_update_lead, mock_unpaid_status_id):
    amocrm_lead.order.set_not_paid()

    order_creator(amocrm_lead)

    mock_update_lead.assert_called_once_with(
        lead_id=amocrm_lead.amocrm_id,
        status_id=mock_unpaid_status_id,
        pipeline_id=777,
        price=amocrm_lead.order.price,
        created_at=amocrm_lead.order.created,
    )


def test_updates_correct_call_for_not_paid_or_unpaid(order_creator, amocrm_lead, mock_update_lead, mock_not_paid_or_unpaid):
    amocrm_lead.order.unpaid = None
    amocrm_lead.order.paid = None
    amocrm_lead.order.save()

    order_creator(amocrm_lead)

    mock_update_lead.assert_called_once_with(
        lead_id=amocrm_lead.amocrm_id,
        status_id=mock_not_paid_or_unpaid,
        pipeline_id=777,
        price=amocrm_lead.order.price,
        created_at=amocrm_lead.order.created,
    )


def test_fails_if_paid_and_transaction_already_exist(order_creator, amocrm_lead, factory):
    amocrm_lead.order.price = 100500
    amocrm_lead.order.save()
    factory.amocrm_order_transaction(order=amocrm_lead.order)

    with pytest.raises(AmoCRMOrderCreatorException, match="Transaction for this paid order already exists"):
        order_creator(amocrm_lead)


def test_fails_if_no_course(order_creator, amocrm_lead):
    amocrm_lead.order.course = None
    amocrm_lead.order.save()

    with pytest.raises(AmoCRMOrderCreatorException, match="Order doesn't have a course"):
        order_creator(amocrm_lead)


def test_fails_if_no_amocrm_course(order_creator, amocrm_lead):
    amocrm_lead.order.course.amocrm_course.delete()
    amocrm_lead.order.refresh_from_db()

    with pytest.raises(AmoCRMOrderCreatorException, match="Course doesn't exist in AmoCRM"):
        order_creator(amocrm_lead)


def test_fails_if_no_amocrm_contact(order_creator, amocrm_lead):
    amocrm_lead.order.user.amocrm_user_contact.delete()
    amocrm_lead.order.refresh_from_db()

    with pytest.raises(AmoCRMOrderCreatorException, match="AmoCRM contact for order's user doesn't exist"):
        order_creator(amocrm_lead)
