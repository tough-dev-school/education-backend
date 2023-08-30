import pytest

from amocrm.models import AmoCRMUser
from amocrm.services.user_pusher import AmoCRMUserPusher

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def _mock_create(mocker):
    mocker.patch("amocrm.dto.customer.AmoCRMCustomer.create", return_value=(4444, 5555))


@pytest.fixture
def mock_update(mocker):
    return mocker.patch("amocrm.dto.customer.AmoCRMCustomer.update")


@pytest.mark.usefixtures("_mock_create")
def test_create_user(user):
    AmoCRMUserPusher(user=user)()

    amocrm_user = AmoCRMUser.objects.get()
    assert amocrm_user.customer_id == 4444
    assert amocrm_user.contact_id == 5555


@pytest.mark.usefixtures("amocrm_user")
def test_update_user(user, mock_update):
    AmoCRMUserPusher(user=user)()

    mock_update.assert_called_once()
