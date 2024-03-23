import pytest

from apps.amocrm.dto import AmoCRMGroupsDTO
from apps.products.models import Group

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def _successful_response(patch):
    patch.return_value = {
        "_total_items": 1,
        "_embedded": {
            "custom_fields": [
                {
                    "id": 2235149,
                    "name": "Группа",
                    "type": "category",
                    "account_id": 31204626,
                    "code": "GROUP",
                    "sort": 511,
                    "is_api_only": False,
                    "enums": None,
                    "request_id": "0",
                    "catalog_id": 11271,
                    "is_visible": True,
                    "triggers": [],
                    "is_deletable": False,
                    "is_required": False,
                    "search_in": None,
                    "nested": [
                        {"id": 6453, "parent_id": None, "value": "popug", "sort": 0},
                        {"id": 6457, "parent_id": None, "value": "hehe", "sort": 1},
                    ],
                    "entity_type": "catalogs",
                    "_links": {"self": {"href": "https://test.amocrm.ru/api/v4/catalogs/11271/custom_fields/2235149"}},
                }
            ]
        },
    }


@pytest.mark.usefixtures("_successful_response")
def test_response_as_list_of_pairs():
    groups = Group.objects.all()

    got = AmoCRMGroupsDTO(groups=groups).push()

    assert got == [("popug", 6453), ("hehe", 6457)]


@pytest.mark.usefixtures("_amocrm_groups")
def test_call_with_id_if_already_exist(patch):
    groups = Group.objects.all()

    AmoCRMGroupsDTO(groups=groups).push()

    patch.assert_called_once_with(
        url="/api/v4/catalogs/900/custom_fields",
        data=[
            {
                "id": 800,
                "nested": [
                    {"value": "popug"},
                    {"id": 333, "value": "hehe"},
                ],
            },
        ],
    )
