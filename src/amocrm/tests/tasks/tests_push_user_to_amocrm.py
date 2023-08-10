import pytest

from amocrm import tasks

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def mock_push_customer(mocker):
    return mocker.patch("amocrm.tasks._push_customer.si")


@pytest.fixture
def mock_push_contact(mocker):
    return mocker.patch("amocrm.tasks._push_contact.si")


@pytest.fixture
def mock_link_contact_to_user(mocker):
    return mocker.patch("amocrm.tasks._link_contact_to_user.si")


@pytest.fixture
def mock_chain(mocker):
    return mocker.patch("amocrm.tasks.chain")


@pytest.mark.parametrize("orders_count", [1, 5, 9])
def test_call_with_orders(user, mock_push_contact, mock_link_contact_to_user, mock_push_customer, mock_chain, orders_count, factory):
    factory.cycle(orders_count).order(user=user)

    tasks.push_user_to_amocrm(user_id=user.id)

    mock_chain.assert_called_once_with(
        mock_push_customer(user_id=99),
        mock_push_contact(user_id=99),
        mock_link_contact_to_user(user_id=99),
    )


def test_doesnt_call_without_orders(user, mock_push_contact, mock_link_contact_to_user, mock_push_customer, mock_chain):
    tasks.push_user_to_amocrm(user_id=user.id)

    mock_chain.assert_not_called()
    mock_push_customer.assert_not_called()
    mock_push_contact.assert_not_called()
    mock_link_contact_to_user.assert_not_called()
