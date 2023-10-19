import pytest

from apps.amocrm.services.group_pusher import AmoCRMGroupsPusher
from apps.products.models import Group

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def mock_group_push(mocker):
    return mocker.patch("apps.amocrm.dto.groups.AmoCRMGroups.push", return_value=[("popug", 444), ("hehe", 333)])


@pytest.mark.usefixtures("_amocrm_groups")
def test_save_amocrm_groups():
    AmoCRMGroupsPusher()()

    assert Group.objects.get(slug="popug").amocrm_group.amocrm_id == 444
    assert Group.objects.get(slug="hehe").amocrm_group.amocrm_id == 333
