from functools import partial

import pytest
from django.contrib.admin.models import ADDITION, LogEntry
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from apps.b2b.models import Student
from apps.b2b.services import BulkStudentCreator, DealCompleter
from apps.orders.models import Order

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def creator(deal):
    return partial(BulkStudentCreator, deal=deal, user_input="first@domain.com, second@domain.com")


@pytest.fixture
def completer():
    return DealCompleter


@pytest.mark.parametrize(
    "input",
    [
        "first@domain.com\nsecond@domain.com",
        "first@domain.com, second@domain.com",
        "first@domain.com; second@domain.com",
        "first@domain.com; second@domain.com.",  # dot at the end
        "\nfirst@domain.com\n\nsecond@domain.com",
        "Коллеги, вот список:\nfirst@domain.com\n\nsecond@domain.com",
        "     first@domain.com\n      second@domain.com",  # tabs
    ],
)
def test_user_input(input, creator):
    assert creator().get_emails(input) == [
        "first@domain.com",
        "second@domain.com",
    ]


def test_single_email(creator):
    assert creator().get_emails("single@email.com") == ["single@email.com"]


def test_students_are_created(creator, deal):
    creator()()

    assert deal.students.count() == 2
    assert deal.students.filter(user__email="first@domain.com").exists() is True
    assert deal.students.filter(user__email="second@domain.com").exists() is True


@pytest.mark.auditlog
@pytest.mark.freeze_time
@pytest.mark.usefixtures("_set_current_user")
def test_auditlog_is_written(creator, deal, user):
    creator()()

    logs = list(
        LogEntry.objects.order_by("id")
        .filter(
            content_type_id=ContentType.objects.get_for_model(Student),
        )
        .all()
    )
    assert logs[0].object_id == str(deal.students.get(user__email="first@domain.com").id)
    assert logs[0].change_message == "Student created"
    assert logs[0].action_flag == ADDITION
    assert logs[0].action_time == timezone.now()
    assert logs[0].object_repr is not None
    assert logs[0].user == user

    assert logs[1].object_id == str(deal.students.get(user__email="second@domain.com").id)
    assert logs[1].change_message == "Student created"
    assert logs[1].action_flag == ADDITION
    assert logs[1].action_time == timezone.now()
    assert logs[1].object_repr is not None
    assert logs[1].user == user


def test_existing_users_are_preserved(creator, deal, mixer):
    user = mixer.blend("users.User", email="first@domain.com", first_name="NameTo", last_name="Preserve")

    creator()()

    assert deal.students.count() == 2, "No new students created"

    assert deal.students.get(user=user).user.first_name == "NameTo"
    assert deal.students.get(user=user).user.last_name == "Preserve"
    assert deal.students.get(user=user).user.email == "first@domain.com"


def test_students_are_created_only_once(creator, deal):
    creator()()
    creator()()

    assert deal.students.count() == 2, "No new students created"


def test_student_can_participate_in_multiple_deals(creator, deal, another_deal):
    creator(deal=deal)()
    creator(deal=another_deal)()

    assert deal.students.count() == 2
    assert another_deal.students.count() == 2
    assert set(deal.students.values_list("user", flat=True)) == set(another_deal.students.values_list("user", flat=True)), (
        "same students participate in both deals"
    )


def test_orders_are_created_when_adding_students_completed_deals(creator, completer, deal):
    creator(deal=deal)()
    completer(deal=deal)()

    creator(deal=deal, user_input="new_student_to_add@gmail.com")()  # add one more user

    order = Order.objects.order_by("created").last()

    assert order.user.email == "new_student_to_add@gmail.com"
    assert order.deal == deal
    assert order.paid is None, "order is not paid"
    assert order.shipped is None, "order is not shipped"
    assert order.price == 0
    assert order.item == deal.course


def test_orders_are_created_when_adding_students_to_deals_shipped_without_payment(creator, completer, deal):
    creator(deal=deal)()
    completer(deal=deal, ship_only=True)()

    creator(deal=deal, user_input="new_student_to_add@gmail.com")()  # add one more user

    order = Order.objects.order_by("created").last()

    assert order.user.email == "new_student_to_add@gmail.com"
    assert order.deal == deal
    assert order.paid is None, "order is not paid"
    assert order.shipped is None, "order is not shipped"
    assert order.price == 0
    assert order.item == deal.course


def test_service_outputs_email_count(creator):
    assert creator()() == 2
