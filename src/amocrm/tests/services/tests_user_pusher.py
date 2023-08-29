import pytest

from amocrm.models import AmoCRMUser
from amocrm.models import AmoCRMUserContact
from amocrm.services.user_pusher import AmoCRMUserPusher
from orders.models import Order

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def _mock_fields_id(mocker):
    mocker.patch("amocrm.services.user_pusher.get_contact_field_id", return_value=333)


@pytest.fixture
def mock_create_customer(mocker):
    return mocker.patch("amocrm.client.AmoCRMClient.create_customer", return_value=4815)


@pytest.fixture
def mock_update_customer(mocker):
    return mocker.patch("amocrm.client.AmoCRMClient.update_customer", return_value=4815)


@pytest.fixture
def mock_create_contact(mocker):
    return mocker.patch("amocrm.client.AmoCRMClient.create_contact", return_value=162342)


@pytest.fixture
def mock_update_contact(mocker):
    return mocker.patch("amocrm.client.AmoCRMClient.update_contact", return_value=162342)


@pytest.fixture
def mock_link_customer_contact(mocker):
    return mocker.patch("amocrm.client.AmoCRMClient.link_entity_to_another_entity")


@pytest.fixture
def mock_create_user(mocker):
    return mocker.patch("amocrm.services.user_pusher.AmoCRMUserPusher.create_user")


@pytest.fixture
def mock_update_user(mocker):
    return mocker.patch("amocrm.services.user_pusher.AmoCRMUserPusher.update_user")


@pytest.fixture
def new_user(user, factory):
    factory.order(user=user)
    return user


@pytest.fixture
def existing_user(new_user, amocrm_user, amocrm_user_contact):
    return new_user


def test_create_fresh_user(new_user, mock_create_user):
    AmoCRMUserPusher(user=new_user)()

    mock_create_user.assert_called_once()


def test_update_existing_user(existing_user, mock_update_user):
    AmoCRMUserPusher(user=existing_user)()

    mock_update_user.assert_called_once()


def test_creating_user_creates_customer_and_contact(new_user, mock_create_customer, mock_create_contact, mock_link_customer_contact):
    AmoCRMUserPusher(user=new_user)()

    customer = AmoCRMUser.objects.get()
    contact = AmoCRMUserContact.objects.get()
    assert customer.user == contact.user == new_user
    mock_create_customer.assert_called_once()
    mock_create_contact.assert_called_once()
    mock_link_customer_contact.assert_called_once()


def test_updating_user_calls(existing_user, mock_update_customer, mock_update_contact):
    AmoCRMUserPusher(user=existing_user)()

    mock_update_customer.assert_called_once()
    mock_update_contact.assert_called_once()


def test_not_push_user_without_orders(new_user, mock_create_user, mock_update_user):
    Order.objects.filter(user=new_user).delete()

    AmoCRMUserPusher(user=new_user)()

    mock_create_user.assert_not_called()
    mock_update_user.assert_not_called()
