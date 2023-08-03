import pytest

from amocrm.types import AmoCRMCatalogElement
from amocrm.types import AmoCRMCatalogElementField
from amocrm.types import AmoCRMCatalogElementFieldValue

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.single_thread,
]


@pytest.fixture
def _successful_response(post):
    post.return_value = {
        "_links": {"self": {"href": "https://test.amocrm.ru/api/v4/catalogs/11271/elements"}},
        "_embedded": {
            "elements": [
                {
                    "id": 14229449,
                    "name": "PopugFields",
                    "created_by": 0,
                    "updated_by": 0,
                    "created_at": 1690883956,
                    "updated_at": 1690883956,
                    "is_deleted": None,
                    "custom_fields_values": [
                        {"field_id": 2235143, "field_name": "Артикул", "field_code": "SKU", "field_type": "text", "values": [{"value": "not-hehe"}]},
                        {"field_id": 2235147, "field_name": "Цена", "field_code": "PRICE", "field_type": "price", "values": [{"value": "999.12"}]},
                        {"field_id": 2235151, "field_name": "External ID", "field_code": "EXTERNAL_ID", "field_type": "text", "values": [{"value": "333"}]},
                    ],
                    "catalog_id": 11271,
                    "account_id": 31204626,
                    "request_id": "0",
                    "_links": {"self": {"href": "https://test.amocrm.ru/api/v4/catalogs/11271/elements/14229449?page=1&limit=250"}},
                }
            ]
        },
    }


@pytest.fixture
def element_fields():
    int_field_value = AmoCRMCatalogElementFieldValue(value=333)
    str_field_value = AmoCRMCatalogElementFieldValue(value="not-hehe")
    decimal_field_value = AmoCRMCatalogElementFieldValue(value=999.12)
    return [
        AmoCRMCatalogElementField(field_id=2235143, values=[str_field_value]),
        AmoCRMCatalogElementField(field_id=2235147, values=[decimal_field_value]),
        AmoCRMCatalogElementField(field_id=2235151, values=[int_field_value]),
    ]


@pytest.fixture
def element(element_fields):
    return AmoCRMCatalogElement(name="PopugFields", custom_fields_values=element_fields)


@pytest.mark.usefixtures("_successful_response")
def test_create_catalog_element(user, amocrm_client, element, element_fields):
    got = amocrm_client.create_catalog_element(catalog_id=777, element=element)

    assert got == AmoCRMCatalogElement(
        id=14229449,
        name="PopugFields",
        custom_fields_values=[
            AmoCRMCatalogElementField(field_id=2235143, values=[AmoCRMCatalogElementFieldValue(value="not-hehe")]),
            AmoCRMCatalogElementField(field_id=2235147, values=[AmoCRMCatalogElementFieldValue(value="999.12")]),
            AmoCRMCatalogElementField(field_id=2235151, values=[AmoCRMCatalogElementFieldValue(value="333")]),
        ],
    )


@pytest.mark.usefixtures("_successful_response")
def test_create_catalog_element_post_correct_params(user, amocrm_client, post, element):
    amocrm_client.create_catalog_element(catalog_id=777, element=element)

    post.assert_called_once_with(
        url="/api/v4/catalogs/777/elements",
        data=[
            {
                "name": "PopugFields",
                "custom_fields_values": [
                    {"field_id": 2235143, "values": [{"value": "not-hehe"}]},
                    {"field_id": 2235147, "values": [{"value": "999.12"}]},
                    {"field_id": 2235151, "values": [{"value": "333"}]},
                ],
            },
        ],
    )
