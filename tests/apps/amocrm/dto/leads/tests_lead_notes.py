import pytest

from apps.amocrm.dto import AmoCRMLead

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def _successful_create_lead_note_response(post):
    post.return_value = {
        "_links": {"self": {"href": "https://thelord.amocrm.ru/api/v4/leads/1781381/notes"}},
        "_embedded": {
            "notes": [
                {
                    "id": 1949919,
                    "entity_id": 1781381,
                    "request_id": "0",
                    "_links": {"self": {"href": "https://thelord.amocrm.ru/api/v4/leads/1781381/notes/1949919"}},
                }
            ]
        },
    }


@pytest.fixture
def dto(order_with_lead):
    return AmoCRMLead(order=order_with_lead)


@pytest.mark.usefixtures("_successful_create_lead_note_response")
def test_create_lead_note_call_amo_crm_client_with_correct_params(dto, post, order_with_lead):
    got = dto.create_note(
        service_name="🤖 🏦 🤖",
        note_text="Оплата отклонена, т.к. клиент хочет заплатить слишком много",
    )

    assert got == 1949919
    post.assert_called_once_with(
        url=f"/api/v4/leads/{order_with_lead.amocrm_lead.amocrm_id}/notes",
        data=[
            {
                "note_type": "service_message",
                "params": {
                    "service": "🤖 🏦 🤖",
                    "text": "Оплата отклонена, т.к. клиент хочет заплатить слишком много",
                },
            },
        ],
    )
