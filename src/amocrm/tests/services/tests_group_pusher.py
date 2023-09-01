import pytest

from amocrm.services.group_pusher import AmoCRMGroupPusher
from products.models import Group

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def mock_group_push(mocker):
    return mocker.patch("amocrm.dto.group.AmoCRMGroup.push", return_value={"popug": 444, "hehe": 333})


@pytest.mark.usefixtures("_groups", "mock_group_push")
def test_save_amocrm_groups():
    AmoCRMGroupPusher()()

    assert Group.objects.get(slug="popug").amocrm_group.amocrm_id == 444
    assert Group.objects.get(slug="hehe").amocrm_group.amocrm_id == 333
