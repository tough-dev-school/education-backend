import pytest

from amocrm.types import AmoCRMCatalogField

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.single_thread,
]


@pytest.fixture
def _successful_response(get):
    get.return_value = {
        "_total_items": 3,
        "_page": 1,
        "_page_count": 1,
        "_links": {"self": {"href": "https://test.amocrm.ru/api/v4/contacts/custom_fields?page=1&limit=250"}},
        "_embedded": {
            "custom_fields": [
                {
                    "id": 2199813,
                    "name": "Должность",
                    "type": "text",
                    "account_id": 31204626,
                    "code": "POSITION",
                    "sort": 2,
                    "is_api_only": False,
                    "enums": None,
                    "group_id": None,
                    "required_statuses": [],
                    "is_deletable": False,
                    "is_predefined": True,
                    "entity_type": "contacts",
                    "remind": None,
                    "triggers": [],
                    "currency": None,
                    "hidden_statuses": [],
                    "_links": {"self": {"href": "https://test.amocrm.ru/api/v4/contacts/custom_fields/2199813?page=1&limit=250"}},
                },
                {
                    "id": 2199815,
                    "name": "Телефон",
                    "type": "multitext",
                    "account_id": 31204626,
                    "code": "PHONE",
                    "sort": 4,
                    "is_api_only": False,
                    "enums": [
                        {"id": 4831029, "value": "WORK", "sort": 2},
                        {"id": 4831031, "value": "WORKDD", "sort": 4},
                        {"id": 4831033, "value": "MOB", "sort": 6},
                        {"id": 4831035, "value": "FAX", "sort": 8},
                        {"id": 4831037, "value": "HOME", "sort": 10},
                        {"id": 4831039, "value": "OTHER", "sort": 12},
                    ],
                    "group_id": None,
                    "required_statuses": [],
                    "is_deletable": False,
                    "is_predefined": True,
                    "entity_type": "contacts",
                    "remind": None,
                    "triggers": [],
                    "currency": None,
                    "hidden_statuses": [],
                    "_links": {"self": {"href": "https://test.amocrm.ru/api/v4/contacts/custom_fields/2199815?page=1&limit=250"}},
                },
                {
                    "id": 2199817,
                    "name": "Email",
                    "type": "multitext",
                    "account_id": 31204626,
                    "code": "EMAIL",
                    "sort": 6,
                    "is_api_only": False,
                    "enums": [
                        {"id": 4831041, "value": "WORK", "sort": 2},
                        {"id": 4831043, "value": "PRIV", "sort": 4},
                        {"id": 4831045, "value": "OTHER", "sort": 6},
                    ],
                    "group_id": None,
                    "required_statuses": [],
                    "is_deletable": False,
                    "is_predefined": True,
                    "entity_type": "contacts",
                    "remind": None,
                    "triggers": [],
                    "currency": None,
                    "hidden_statuses": [],
                    "_links": {"self": {"href": "https://test.amocrm.ru/api/v4/contacts/custom_fields/2199817?page=1&limit=250"}},
                },
            ]
        },
    }


@pytest.mark.usefixtures("_successful_response")
def test_get_contact_fields(user, amocrm_client, get):
    got = amocrm_client.get_contact_fields()

    assert got == [
        AmoCRMCatalogField(id=2199813, name="Должность", type="text", code="POSITION", nested=None),
        AmoCRMCatalogField(id=2199815, name="Телефон", type="multitext", code="PHONE", nested=None),
        AmoCRMCatalogField(id=2199817, name="Email", type="multitext", code="EMAIL", nested=None),
    ]
    get.assert_called_once_with(
        url="/api/v4/contacts/custom_fields",
        params={"limit": 250},
    )
