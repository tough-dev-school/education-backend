import pytest

from apps.amocrm.dto import AmoCRMNoteConnector


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
def connector():
    return AmoCRMNoteConnector()


@pytest.mark.usefixtures("_successful_create_lead_note_response")
def test_create_lead_note_call_amo_crm_client_with_correct_params(connector, post):
    got = connector.create_lead_note(
        lead_id=1781381,
        service_name="🤖 🏦 🤖",
        note_text="Оплата отклонена, т.к. клиент хочет заплатить слишком много",
    )

    assert got == 1949919
    post.assert_called_once_with(
        url="/api/v4/leads/1781381/notes",
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
