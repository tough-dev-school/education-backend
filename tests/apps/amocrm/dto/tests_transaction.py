import pytest

from apps.amocrm.dto import AmoCRMTransactionDTO

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def _successful_create_transaction_response(post):
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


@pytest.mark.usefixtures("_successful_create_transaction_response")
def test_create(order):
    transaction_id = AmoCRMTransactionDTO(order=order).create()

    assert transaction_id == 684537


def test_create_call(order, post):
    AmoCRMTransactionDTO(order=order).create()

    post.assert_called_once_with(
        url="/api/v4/customers/4444/transactions",
        data=[
            {
                "comment": "Order slug in lms: Gu2g7SXFxfepif4UkLNhzx",
                "price": 100,
                "_embedded": {
                    "catalog_elements": [
                        {
                            "id": 999111,
                            "metadata": {
                                "catalog_id": 900,
                                "quantity": 1,
                            },
                        },
                    ],
                },
            },
        ],
    )


def test_delete_call(order, delete):
    AmoCRMTransactionDTO(order=order).delete()

    delete.assert_called_once_with(
        url="/api/v4/customers/transactions/22222",
        expected_status_codes=[204],
    )
