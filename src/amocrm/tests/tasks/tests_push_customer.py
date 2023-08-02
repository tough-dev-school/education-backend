import pytest

from amocrm import tasks
from amocrm.models import AmoCRMUser

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def mock_create_customer(mocker):
    return mocker.patch("amocrm.client.AmoCRMClient.create_customer", return_value=4815)


@pytest.fixture
def mock_update_customer(mocker):
    return mocker.patch("amocrm.client.AmoCRMClient.update_customer", return_value=4815)


def test_call_creates_customer_if_not_amocrm_user(user, mock_create_customer, mock_update_customer):
    tasks.push_customer(user_id=user.id)

    mock_create_customer.assert_called_once_with(user=user)
    mock_update_customer.assert_not_called()


@pytest.mark.usefixtures("mock_create_customer")
def test_creates_customer_if_not_amocrm_user(user):
    tasks.push_customer(user_id=user.id)

    amocrm_user = AmoCRMUser.objects.get()
    assert amocrm_user.amocrm_id == 4815
    assert amocrm_user.user == user


def test_call_updates_customer_if_amocrm_user_exists(amocrm_user, mock_create_customer, mock_update_customer):
    tasks.push_customer(user_id=amocrm_user.user.id)

    mock_update_customer.assert_called_once_with(amocrm_user=amocrm_user)
    mock_create_customer.assert_not_called()
