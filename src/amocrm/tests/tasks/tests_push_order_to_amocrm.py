import pytest

from amocrm import tasks

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def mock_push_lead(mocker):
    return mocker.patch("amocrm.tasks._push_lead.si")


@pytest.fixture
def mock_push_transaction(mocker):
    return mocker.patch("amocrm.tasks._push_transaction.si")


@pytest.fixture
def mock_link_course_to_lead(mocker):
    return mocker.patch("amocrm.tasks._link_course_to_lead.si")


@pytest.fixture
def mock_chain(mocker):
    return mocker.patch("amocrm.tasks.chain")


@pytest.fixture
def order_with_lead(factory):
    order = factory.order(id=99)
    factory.amocrm_order_lead(order=order)
    return order


@pytest.fixture
def order_with_lead_and_transaction(factory):
    order = factory.order(id=99)
    factory.amocrm_order_lead(order=order)
    factory.amocrm_order_transaction(order=order)
    return order


@pytest.fixture
def order_without_lead_and_transaction(factory):
    return factory.order(id=99)


def test_call_with_lead(order_with_lead, mock_push_lead, mock_push_transaction, mock_link_course_to_lead, mock_chain):
    tasks.push_order_to_amocrm(order_id=order_with_lead.id)

    mock_chain.assert_called_once_with(
        mock_link_course_to_lead(order_id=99),
        mock_push_lead(order_id=99),
        mock_push_transaction(order_id=99),
    )


def test_call_without_lead_and_transaction(order_without_lead_and_transaction, mock_push_lead, mock_push_transaction, mock_link_course_to_lead, mock_chain):
    tasks.push_order_to_amocrm(order_id=order_without_lead_and_transaction.id)

    mock_chain.assert_called_once_with(
        mock_push_lead(order_id=99),
        mock_link_course_to_lead(order_id=99),
        mock_push_lead(order_id=99),
        mock_push_transaction(order_id=99),
    )


def test_doesnt_call_with_transaction(order_with_lead_and_transaction, mock_push_lead, mock_push_transaction, mock_link_course_to_lead, mock_chain):
    tasks.push_order_to_amocrm(order_id=order_with_lead_and_transaction.id)

    mock_chain.assert_not_called()
    mock_push_lead.assert_not_called()
    mock_push_transaction.assert_not_called()
    mock_link_course_to_lead.assert_not_called()
