from datetime import datetime, timedelta

import pytest

from apps.amocrm import types
from apps.amocrm.services.orders.order_task_creator import (
    AmoCRMOrderTaskCreator,
    AmoCRMOrderTaskCreatorException,
    AmoCRMOrderTaskData,
    AmoCRMOrderTaskDataServiceNote,
)
from apps.orders.models import Order
from core.exceptions import AppServiceException

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def mock_user_operator_get(mocker):
    return mocker.patch(
        "apps.amocrm.dto.user_operator.AmoCRMUserOperatorDTO.get",
        return_value=[
            types.UserOperator(id=777666, name="Сашка Сидоров", email="sashka@example.com"),
            types.UserOperator(id=888777, name="Петруша Иванов", email="petrusha@example.com"),
        ],
    )


@pytest.fixture(autouse=True)
def mock_lead_task_get(mocker):
    return mocker.patch(
        "apps.amocrm.dto.lead_task.AmoCRMLeadTaskDTO.get",
        return_value=[],
    )


@pytest.fixture(autouse=True)
def mock_lead_task_create(mocker):
    return mocker.patch(
        "apps.amocrm.dto.lead_task.AmoCRMLeadTaskDTO.create",
        return_value=777,
    )


@pytest.fixture(autouse=True)
def mock_lead_note_create_service_message(mocker):
    return mocker.patch(
        "apps.amocrm.dto.lead_note.AmoCRMLeadNoteDTO.create_service_message",
        return_value=99999,
    )


@pytest.fixture
def create_service_note_data():
    def create(**kwargs):
        return AmoCRMOrderTaskDataServiceNote(
            service_name=kwargs.get("service_name", "🤖"),
            service_note=kwargs.get("service_note", "Cлишком много платите"),
        )

    return create


@pytest.fixture
def create_order_task_data(create_service_note_data):
    def create(**kwargs):
        test_data = {
            "task_name": "Отказ платёжной системы",
            "task_type_id": types.TaskType.CONTACT,
            "task_responsible_user_email": "petrusha@example.com",
            "service_note": create_service_note_data(),
        }

        test_data.update(kwargs)

        return AmoCRMOrderTaskData(**test_data)

    return create


@pytest.fixture
def payment_rejected_task_data(create_order_task_data):
    return create_order_task_data()


@pytest.fixture
def order_with_lead(order, amocrm_lead):
    order.update(amocrm_lead=amocrm_lead)
    return order


@pytest.fixture
def task_creator(order_with_lead, payment_rejected_task_data):
    return lambda order=order_with_lead, task_data=payment_rejected_task_data: AmoCRMOrderTaskCreator(
        order=order,
        task_data=task_data,
    )()


@pytest.mark.freeze_time("2024-01-01 00:00:00Z")
def test_create_amocrm_lead_task_and_lead_note_service_message(task_creator, mock_lead_task_create, mock_lead_note_create_service_message, amocrm_lead) -> None:
    task_creator()

    mock_lead_note_create_service_message.assert_called_once_with(
        lead_id=amocrm_lead.amocrm_id,
        service_name="🤖",
        note_text="Cлишком много платите",
    )
    mock_lead_task_create.assert_called_once_with(
        lead_id=amocrm_lead.amocrm_id,
        task_type_id=types.TaskType.CONTACT,
        task_text="Отказ платёжной системы",
        timestamp_complete_till=int(datetime(2024, 1, 4, 0, 0, 0).timestamp()),  # 3 days deadline by default
        responsible_user_id=888777,
    )


@pytest.mark.freeze_time("2024-01-01 00:00:00Z")
def test_create_amocrm_lead_task_with_custom_deadline_if_it_set(task_creator, mock_lead_task_create, create_order_task_data, mocker) -> None:
    task_data = create_order_task_data(task_deadline_timedelta=timedelta(days=5))

    task_creator(task_data=task_data)

    mock_lead_task_create.assert_called_once_with(
        lead_id=mocker.ANY,
        task_type_id=mocker.ANY,
        task_text=mocker.ANY,
        timestamp_complete_till=int(datetime(2024, 1, 6, 0, 0, 0).timestamp()),  # 5 days as deadline timedelta
        responsible_user_id=mocker.ANY,
    )


def test_do_not_create_amocrm_task_if_it_exists_already(task_creator, mock_lead_task_get, mock_lead_task_create, mock_lead_note_create_service_message) -> None:
    mock_lead_task_get.return_value = [
        types.Task(id=100500, task_type_id=types.TaskType.CONTACT, text="Отказ платёжной системы", is_completed=False),
    ]

    task_creator()

    mock_lead_task_create.assert_not_called()
    mock_lead_note_create_service_message.assert_called_once(), "Service note should be created despite the task already exists"


@pytest.mark.parametrize(
    ("task_type_id", "task_text"),
    [
        (types.TaskType.MEETING, "Отказ платёжной системы"),  # Same text, but different type
        (types.TaskType.CONTACT, "Позвонить клиенту"),  # Same type but different text
    ],
)
def test_create_amocrm_task_if_other_task_exists_but_text_not_matched(task_creator, mock_lead_task_get, mock_lead_task_create, task_text, task_type_id) -> None:
    mock_lead_task_get.return_value = [
        types.Task(id=100500, task_type_id=task_type_id, text=task_text, is_completed=False),
    ]

    task_creator()

    mock_lead_task_create.assert_called_once()


def test_do_not_create_lead_note_service_message_service_note_not_provided(task_creator, mock_lead_note_create_service_message, create_order_task_data) -> None:
    task_data = create_order_task_data(service_note=None)

    task_creator(task_data=task_data)

    mock_lead_note_create_service_message.assert_not_called()


def test_same_deal_order_without_lead_not_fail(task_creator, user, course, factory, mock_lead_note_create_service_message, mock_lead_task_create) -> None:
    same_lead_order_previously_linked_with_amocrm_lead = factory.order(user=user, item=course, amocrm_lead=None)

    task_creator(order=same_lead_order_previously_linked_with_amocrm_lead)

    mock_lead_note_create_service_message.assert_called_once()
    mock_lead_task_create.assert_called_once()


def test_call_lead_task_dto_get_with_correct_params(task_creator, mock_lead_task_get, mocker) -> None:
    task_creator()

    mock_lead_task_get.assert_called_once_with(
        lead_id=mocker.ANY,
        is_completed=False,  # only not completed tasks should be checked
    )


def test_raise_if_responsible_user_email_not_exists_in_amocrm_user_operators(task_creator, create_order_task_data, mock_user_operator_get) -> None:
    task_data = create_order_task_data(task_responsible_user_email="petrovich@email.com")

    with pytest.raises(AmoCRMOrderTaskCreatorException, match="There is no AmoCRM operators with email"):
        task_creator(task_data=task_data)

    mock_user_operator_get.assert_called_once()


def test_raise_if_order_or_same_deal_orders_not_linked_with_amocrm_lead(task_creator, order_with_lead) -> None:
    order_with_lead.update(amocrm_lead=None)
    Order.objects.same_deal(order_with_lead).update(amocrm_lead=None)

    with pytest.raises(AmoCRMOrderTaskCreatorException, match="There is no AmoCRM lead linked to order's deal") as exc_info:
        task_creator()

    assert not isinstance(exc_info.value, AppServiceException), "Should not be AppServiceException cause it's programming error"
