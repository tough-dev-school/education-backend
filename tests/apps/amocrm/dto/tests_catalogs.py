import pytest

from apps.amocrm import types
from apps.amocrm.dto.catalogs import AmoCRMCatalogsDTO

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def _successful_get_catalogs_response(get):
    get.return_value = {
        "_links": {"self": {"href": "/api/v4/catalogs", "method": "get"}},
        "_embedded": {
            "catalogs": [
                {
                    "id": 11271,
                    "name": "Товары",
                    "created_by": 9898394,
                    "created_at": 1690790026,
                    "sort": 0,
                    "type": "products",
                    "can_add_elements": True,
                    "can_show_in_cards": True,
                    "can_link_multiple": True,
                    "sdk_widget_code": None,
                    "widgets": [],
                    "_links": {"self": {"href": "/api/v4/catalogs?id=11271", "method": "get"}},
                },
                {
                    "id": 11273,
                    "name": "Мои юр. лица",
                    "created_by": 9898394,
                    "created_at": 1690790026,
                    "sort": 0,
                    "type": "suppliers",
                    "can_add_elements": True,
                    "can_show_in_cards": True,
                    "can_link_multiple": True,
                    "sdk_widget_code": None,
                    "widgets": [],
                    "_links": {"self": {"href": "/api/v4/catalogs?id=11273", "method": "get"}},
                },
            ]
        },
    }


@pytest.fixture
def _successful_get_fields_response(get):
    get.return_value = {
        "_total_items": 5,
        "_page": 1,
        "_page_count": 1,
        "_links": {"self": {"href": "https://test.amocrm.ru/api/v4/catalogs/11271/custom_fields?limit=250&page=1"}},
        "_embedded": {
            "custom_fields": [
                {
                    "id": 2235143,
                    "name": "Артикул",
                    "type": "text",
                    "account_id": 31204626,
                    "code": "SKU",
                    "sort": 510,
                    "is_api_only": False,
                    "enums": None,
                    "catalog_id": 11271,
                    "is_visible": True,
                    "triggers": [],
                    "is_deletable": False,
                    "is_required": False,
                    "search_in": None,
                    "nested": None,
                    "entity_type": "catalogs",
                    "_links": {"self": {"href": "https://test.amocrm.ru/api/v4/catalogs/11271/custom_fields/2235143?limit=250&page=1"}},
                },
                {
                    "id": 2235149,
                    "name": "Группа",
                    "type": "category",
                    "account_id": 31204626,
                    "code": "GROUP",
                    "sort": 511,
                    "is_api_only": False,
                    "enums": None,
                    "catalog_id": 11271,
                    "is_visible": True,
                    "triggers": [],
                    "is_deletable": False,
                    "is_required": False,
                    "search_in": None,
                    "nested": [{"id": 6319, "parent_id": None, "value": "popug", "sort": 0}, {"id": 6321, "parent_id": None, "value": "testtest", "sort": 1}],
                    "entity_type": "catalogs",
                    "_links": {"self": {"href": "https://test.amocrm.ru/api/v4/catalogs/11271/custom_fields/2235149?limit=250&page=1"}},
                },
            ]
        },
    }


@pytest.mark.usefixtures("_successful_get_catalogs_response")
def test_get_returns_list_of_catalogs(get):
    got = AmoCRMCatalogsDTO.get()

    assert got == [
        types.Catalog(id=11271, name="Товары", type="products"),
        types.Catalog(id=11273, name="Мои юр. лица", type="suppliers"),
    ]


def test_get_catalogs_call_url(get):
    AmoCRMCatalogsDTO.get()

    get.assert_called_once_with(
        url="/api/v4/catalogs",
        params={"limit": 250},
        cached=True,
    )


@pytest.mark.usefixtures("_successful_get_fields_response")
def test_get_fields_returns_list_of_fields(get):
    got = AmoCRMCatalogsDTO.get_fields(catalog_id=777)

    assert got == [
        types.CatalogField(id=2235143, code="SKU"),
        types.CatalogField(id=2235149, code="GROUP"),
    ]


def test_get_fields_call_url(get):
    AmoCRMCatalogsDTO.get_fields(catalog_id=777)

    get.assert_called_once_with(
        url="/api/v4/catalogs/777/custom_fields",
        params={"limit": 250},
        cached=True,
    )


@pytest.mark.usefixtures("_successful_get_fields_response")
def test_get_contacts_fields_returns_list_of_fields(get):
    got = AmoCRMCatalogsDTO.get_contacts_fields()

    assert got == [
        types.CatalogField(id=2235143, code="SKU"),
        types.CatalogField(id=2235149, code="GROUP"),
    ]


def test_get_contacts_fields_call_url(get):
    AmoCRMCatalogsDTO.get_contacts_fields()

    get.assert_called_once_with(
        url="/api/v4/contacts/custom_fields",
        params={"limit": 250},
        cached=True,
    )
