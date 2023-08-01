import pytest

from amocrm.types import AmoCRMCatalogFieldValue

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.single_thread,
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


@pytest.fixture
def field_values():
    return [
        AmoCRMCatalogFieldValue(id=6453, value="popug"),
        AmoCRMCatalogFieldValue(value="hehe"),
    ]


@pytest.mark.usefixtures("_successful_response")
def test_update_catalog_field(user, amocrm_client, patch, field_values):
    got = amocrm_client.update_catalog_field(catalog_id=777, field_id=333, field_values=field_values)

    assert got == [
        AmoCRMCatalogFieldValue(id=6453, value="popug"),
        AmoCRMCatalogFieldValue(id=6457, value="hehe"),
    ]
    patch.assert_called_once_with(
        url="/api/v4/catalogs/777/custom_fields",
        data=[
            {
                "id": 333,
                "nested": [
                    {"id": 6453, "value": "popug"},
                    {"value": "hehe"},
                ],
            },
        ],
    )
