import pytest

from _decimal import Decimal

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.single_thread,
]


@pytest.fixture
def _successful_response(patch):
    patch.return_value = {
        "_links": {"self": {"href": "https://test.amocrm.ru/api/v4/leads"}},
        "_embedded": {"leads": [{"id": 3, "updated_at": 1691492542, "_links": {"self": {"href": "https://test.amocrm.ru/api/v4/leads/41353987"}}}]},
    }


@pytest.mark.usefixtures("_successful_response")
def test_update_lead_request_fields(amocrm_client, patch):
    got = amocrm_client.update_lead(
        lead_id=3,
        status_id=6,
        price=Decimal(90.00),
    )

    assert got == 3
    patch.assert_called_once_with(
        url="/api/v4/leads",
        data=[
            {
                "id": 3,
                "status_id": 6,
                "price": 90,
            },
        ],
    )
