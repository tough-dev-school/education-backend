import pytest

from apps.amocrm import types
from apps.amocrm.dto import AmoCRMUserOperatorDTO


@pytest.fixture(autouse=True)
def _successful_get_users_response(get):
    get.return_value = {
        "_total_items": 1,
        "_page": 1,
        "_page_count": 1,
        "_links": {"self": {"href": "https://thelord.amocrm.ru/api/v4/users/?page=1&limit=250"}},
        "_embedded": {
            "users": [
                {
                    "id": 10450722,
                    "name": "Петруша Иванов",
                    "email": "petrusha@ivanov.ru",
                    "lang": "ru",
                    "rights": {
                        "leads": {"view": "A", "edit": "A", "add": "A", "delete": "A", "export": "A"},
                        "contacts": {"view": "A", "edit": "A", "add": "A", "delete": "A", "export": "A"},
                        "companies": {"view": "A", "edit": "A", "add": "A", "delete": "A", "export": "A"},
                        "tasks": {"edit": "A", "delete": "A"},
                        "mail_access": False,
                        "catalog_access": False,
                        "files_access": False,
                        "status_rights": [
                            {"entity_type": "leads", "pipeline_id": 7575470, "status_id": 62729374, "rights": {"view": "A", "edit": "A", "delete": "A"}}
                        ],
                        "catalog_rights": None,
                        "custom_fields_rights": None,
                        "oper_day_reports_view_access": False,
                        "oper_day_user_tracking": False,
                        "is_admin": False,
                        "is_free": False,
                        "is_active": True,
                        "group_id": None,
                        "role_id": None,
                    },
                    "_links": {"self": {"href": "https://thelord.amocrm.ru/api/v4/users/10450722/?page=1&limit=250"}},
                },
            ]
        },
    }


@pytest.fixture
def dto():
    return AmoCRMUserOperatorDTO()


def test_amo_crm_operator_dto_return_users(dto):
    got = dto.get()

    assert got == [
        types.UserOperator(
            id=10450722,
            name="Петруша Иванов",
            email="petrusha@ivanov.ru",
        ),
    ]


def test_amo_crm_operator_call_amo_client_with_correct_params(dto, get):
    dto.get()

    get.assert_called_once_with(
        url="/api/v4/users",
        params={"limit": 250},
        cached=True,
    )
