import pytest

from amocrm.dto import AmoCRMProduct

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def _successful_create_response(post):
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


@pytest.mark.usefixtures("_successful_create_response")
def test_create_response(course, post):
    got = AmoCRMProduct(course=course).create()

    assert got == 14229449


def test_create_contact(course, post):
    AmoCRMProduct(course=course).create()

    post.assert_called_once_with(
        url="/api/v4/catalogs/900/elements",
        data=[
            {
                "name": "Popug",
                "custom_fields_values": [
                    {"field_id": 800, "values": [{"value": "200"}]},
                    {"field_id": 800, "values": [{"value": "popug-003"}]},
                    {"field_id": 800, "values": [{"value": "шт"}]},
                    {"field_id": 800, "values": [{"value": "popug-group"}]},
                ],
            },
        ],
    )


def test_update(course, patch):
    AmoCRMProduct(course=course).update()

    patch.assert_called_once_with(
        url="/api/v4/catalogs/900/elements",
        data=[
            {
                "id": 999111,
                "name": "Popug",
                "custom_fields_values": [
                    {"field_id": 800, "values": [{"value": "200"}]},
                    {"field_id": 800, "values": [{"value": "popug-003"}]},
                    {"field_id": 800, "values": [{"value": "шт"}]},
                    {"field_id": 800, "values": [{"value": "popug-group"}]},
                ],
            },
        ],
    )
