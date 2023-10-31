from datetime import datetime
import pytest
from zoneinfo import ZoneInfo

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def question(mixer, course):
    question = mixer.blend("homework.Question")
    question.courses.add(course)

    return question


@pytest.fixture
def answer(mixer, user, question):
    return mixer.blend("homework.Answer", question=question, author=user)


@pytest.fixture(autouse=True)
def purchase(factory, course, user):
    return factory.order(
        user=user,
        item=course,
        paid=datetime(2032, 12, 1, 15, 30, tzinfo=ZoneInfo("America/New_York")),  # any timezone should suite here
    )


@pytest.fixture
def latest_purchase(factory, another_course, user):
    return factory.order(
        user=user,
        item=another_course,
        paid=datetime(2035, 12, 1, 15, 30, tzinfo=ZoneInfo("Asia/Magadan")),  # any timezone should suite here
    )


def test_single_course(answer, course):
    assert answer.get_purchased_course() == course


def test_multiple_courses_in_the_homework(answer, course, another_course):
    answer.question.courses.add(another_course)

    assert answer.get_purchased_course() == course


@pytest.mark.usefixtures("latest_purchase")
def test_latest_purchased_is_returned(answer, another_course):
    answer.question.courses.add(another_course)

    assert answer.get_purchased_course() == another_course


def test_purchases_from_another_users_are_ignored(answer, purchase, mixer):
    purchase.user = mixer.blend("users.User")
    purchase.save()

    assert answer.get_purchased_course() is None
