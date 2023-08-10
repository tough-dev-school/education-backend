import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.single_thread,
]


def test_delete_transaction(user, amocrm_client, delete):
    amocrm_client.delete_transaction(transaction_id=789)

    delete.assert_called_once_with(
        url="/api/v4/customers/transactions/789",
        excpected_status_codes=[204],
    )
