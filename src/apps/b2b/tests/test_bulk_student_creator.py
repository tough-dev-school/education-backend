from functools import partial

import pytest

from apps.b2b.services import BulkStudentCreator

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def creator(deal):
    return partial(BulkStudentCreator, deal=deal, user_input="first@domain.com, second@domain.com")


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
    assert deal.students.values_list("user", flat=True) == another_deal.students.values_list("user", flat=True), "same students participate in both deals"


def test_service_outputs_email_count(creator):
    assert creator()() == 2
