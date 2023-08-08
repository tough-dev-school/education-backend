import pytest

from _decimal import Decimal

from amocrm.types import AmoCRMTransactionElement
from amocrm.types import AmoCRMTransactionElementMetadata

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.single_thread,
]


@pytest.fixture
def _successful_response(post):
    post.return_value = {
        "_total_items": 1,
        "_embedded": {
            "transactions": [
                {
                    "id": 684537,
                    "customer_id": 1369371,
                    "request_id": "0",
                    "_links": {"self": {"href": "https://test.amocrm.ru/api/v4/customers/1369371/transactions/684537"}},
                    "_embedded": {"customer": {"id": 1369371, "_links": {"self": {"href": "https://test.amocrm.ru/api/v4/customers/1369371"}}}},
                }
            ]
        },
    }


@pytest.fixture
def purchased_product():
    metadata = AmoCRMTransactionElementMetadata(catalog_id=777, quantity=1)
    return AmoCRMTransactionElement(id=684537, metadata=metadata)


@pytest.mark.usefixtures("_successful_response")
def test_create_lead_request_fields(amocrm_client, post, purchased_product):
    got = amocrm_client.create_customer_transaction(
        customer_id=1369371,
        price=Decimal(100.00),
        order_id=8674674657,
        purchased_product=purchased_product,
    )

    assert got == 684537
    post.assert_called_once_with(
        url="/api/v4/customers/1369371/transactions",
        data=[
            {
                "comment": "Order ID in lms: 8674674657",
                "price": 100,
                "_embedded": {
                    "catalog_elements": [
                        {
                            "id": 684537,
                            "metadata": {
                                "catalog_id": 777,
                                "quantity": 1,
                            },
                        },
                    ],
                },
            },
        ],
    )
