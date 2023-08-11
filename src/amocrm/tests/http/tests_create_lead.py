from datetime import datetime
import pytest

from _decimal import Decimal

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.single_thread,
]


@pytest.fixture
def _successful_response(post):
    post.return_value = [{"id": 41353987, "contact_id": 72845935, "company_id": None, "request_id": ["0"], "merged": False}]


@pytest.mark.usefixtures("_successful_response")
def test_create_lead_request_fields(amocrm_client, post):
    got = amocrm_client.create_lead(
        status_id=7,
        pipeline_id=14,
        contact_id=28,
        price=Decimal(100.00),
        created_at=datetime(2023, 1, 1),
    )

    assert got == 41353987
    post.assert_called_once_with(
        url="/api/v4/leads/complex",
        data=[
            {
                "status_id": 7,
                "pipeline_id": 14,
                "price": 100,
                "created_at": 1672520400,
                "_embedded": {"contacts": [{"id": 28}]},
            },
        ],
    )
