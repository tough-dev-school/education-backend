import pytest

from amocrm.services.orders.order_lead_updater import AmoCRMOrderLeadUpdater
from amocrm.services.orders.order_lead_updater import AmoCRMOrderLeadUpdaterException

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def _mock_b2b_b2c_fields_id(mocker):
    mocker.patch("amocrm.services.orders.order_lead_updater.get_b2b_pipeline_status_id", return_value=888)
    mocker.patch("amocrm.services.orders.order_lead_updater.get_b2c_pipeline_status_id", return_value=999)


@pytest.fixture
def mock_paid_status_id(mocker):
    return mocker.patch("amocrm.services.orders.order_lead_updater.AmoCRMOrderLeadUpdater._paid_status_id", return_value=222)


@pytest.fixture
def mock_unpaid_status_id(mocker):
    return mocker.patch("amocrm.services.orders.order_lead_updater.AmoCRMOrderLeadUpdater._unpaid_status_id", return_value=333)


@pytest.fixture
def mock_not_paid_or_unpaid(mocker):
    return mocker.patch("amocrm.services.orders.order_lead_updater.AmoCRMOrderLeadUpdater._not_paid_or_unpaid_status_id", return_value=444)


@pytest.fixture(autouse=True)
def mock_update_lead(mocker):
    return mocker.patch("amocrm.client.AmoCRMClient.update_lead", return_value=481516)


@pytest.fixture
def lead_updater():
    return lambda amocrm_lead: AmoCRMOrderLeadUpdater(amocrm_lead=amocrm_lead)()


def test_updates_amocrm_order_lead(lead_updater, amocrm_lead):
    got = lead_updater(amocrm_lead)

    assert got == 481516


@pytest.mark.parametrize(("user_tags", "status"), [(["b2b", "any-purchase"], 888), (["any-purchase"], 999)])
def test_updates_correct_call_b2b_or_b2c(lead_updater, amocrm_lead, mock_update_lead, user_tags, status):
    amocrm_lead.order.user.tags = user_tags
    amocrm_lead.order.user.save()

    lead_updater(amocrm_lead)

    mock_update_lead.assert_called_once_with(
        lead_id=amocrm_lead.amocrm_id,
        status_id=status,
        price=amocrm_lead.order.price,
        created_at=amocrm_lead.order.created,
    )


def test_updates_correct_call_for_paid(lead_updater, amocrm_lead, mock_update_lead, mock_paid_status_id):
    amocrm_lead.order.set_paid()

    lead_updater(amocrm_lead)

    mock_update_lead.assert_called_once_with(
        lead_id=amocrm_lead.amocrm_id,
        status_id=mock_paid_status_id,
        price=amocrm_lead.order.price,
        created_at=amocrm_lead.order.created,
    )


def test_updates_correct_call_for_unpaid(lead_updater, amocrm_lead, mock_update_lead, mock_unpaid_status_id):
    amocrm_lead.order.set_not_paid()

    lead_updater(amocrm_lead)

    mock_update_lead.assert_called_once_with(
        lead_id=amocrm_lead.amocrm_id,
        status_id=mock_unpaid_status_id,
        price=amocrm_lead.order.price,
        created_at=amocrm_lead.order.created,
    )


def test_updates_correct_call_for_not_paid_or_unpaid(lead_updater, amocrm_lead, mock_update_lead, mock_not_paid_or_unpaid):
    amocrm_lead.order.unpaid = None
    amocrm_lead.order.paid = None
    amocrm_lead.order.save()

    lead_updater(amocrm_lead)

    mock_update_lead.assert_called_once_with(
        lead_id=amocrm_lead.amocrm_id,
        status_id=mock_not_paid_or_unpaid,
        price=amocrm_lead.order.price,
        created_at=amocrm_lead.order.created,
    )


def test_fails_if_paid_and_transaction_already_exist(lead_updater, amocrm_lead, factory):
    factory.amocrm_order_transaction(order=amocrm_lead.order)

    with pytest.raises(AmoCRMOrderLeadUpdaterException, match="Transaction for this paid order already exists"):
        lead_updater(amocrm_lead)


def test_fails_if_no_course(lead_updater, amocrm_lead):
    amocrm_lead.order.course = None
    amocrm_lead.order.save()

    with pytest.raises(AmoCRMOrderLeadUpdaterException, match="Order doesn't have a course"):
        lead_updater(amocrm_lead)


def test_fails_if_no_amocrm_course(lead_updater, amocrm_lead):
    amocrm_lead.order.course.amocrm_course.delete()
    amocrm_lead.order.refresh_from_db()

    with pytest.raises(AmoCRMOrderLeadUpdaterException, match="Course doesn't exist in AmoCRM"):
        lead_updater(amocrm_lead)


def test_fails_if_no_amocrm_contact(lead_updater, amocrm_lead):
    amocrm_lead.order.user.amocrm_user_contact.delete()
    amocrm_lead.order.refresh_from_db()

    with pytest.raises(AmoCRMOrderLeadUpdaterException, match="AmoCRM contact for order's user doesn't exist"):
        lead_updater(amocrm_lead)
