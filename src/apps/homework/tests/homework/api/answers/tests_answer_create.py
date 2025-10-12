from datetime import datetime, timezone

import pytest

from apps.homework.models import Answer

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("purchase"),
]

JSON = {
    "type": "doc",
    "content": [
        {
            "type": "paragraph",
            "content": [
                {
                    "type": "text",
                    "text": "Горите в аду",
                }
            ],
        }
    ],
}


@pytest.fixture
def _no_purchase(purchase):
    purchase.unship()


def get_answer():
    return Answer.objects.last()


def test_creation_with_json(api, question, another_answer, purchase):
    """Drop it when you remove the 'text' field"""
    api.post(
        "/api/v2/homework/answers/",
        {
            "content": JSON,
            "question": question.slug,
            "parent": another_answer.slug,
        },
    )

    created = get_answer()

    assert created.question == question
    assert created.parent == another_answer
    assert created.author == api.user
    assert created.study == purchase.study
    assert created.content == JSON
    assert created.text == "Горите в аду"


def test_no_json(api, question, another_answer):
    api.post(
        "/api/v2/homework/answers/",
        {
            "question": question.slug,
            "parent": another_answer.slug,
        },
        expected_status_code=400,
    )


def test_no_question(api, another_answer):
    api.post(
        "/api/v2/homework/answers/",
        {
            "content": JSON,
            "parent": another_answer.slug,
        },
        expected_status_code=400,
    )


@pytest.mark.parametrize(
    "shit",
    [
        "",
        "text",
        ["a"],
        '{"a": "b"}',
    ],
)
def test_invalid_json(api, another_answer, question, shit):
    api.post(
        "/api/v2/homework/answers/",
        {
            "content": shit,
            "parent": another_answer.slug,
            "question": question.slug,
        },
        expected_status_code=400,
    )


@pytest.mark.usefixtures("kamchatka_timezone")
@pytest.mark.freeze_time("2023-01-23 08:30:40+12:00")
def test_create_answer_fields(api, question, another_answer):
    got = api.post(
        "/api/v2/homework/answers/",
        {
            "content": JSON,
            "question": question.slug,
            "parent": another_answer.slug,
        },
    )

    assert got["created"] == "2023-01-23T08:30:40+12:00"
    assert got["modified"] == "2023-01-23T08:30:40+12:00"
    assert "-4" in got["slug"]
    assert got["question"] == str(question.slug)
    assert got["author"]["uuid"] == str(api.user.uuid)
    assert got["author"]["first_name"] == api.user.first_name
    assert got["author"]["last_name"] == api.user.last_name
    assert got["parent"] == str(another_answer.slug)
    assert got["content"] == JSON
    assert got["has_descendants"] is False  # newly created answer couldn't have descendants
    assert got["is_editable"] is True  # and should be editable
    assert got["reactions"] == []  # and couldn't have reactions


def test_creating_root_answer(api, question):
    api.post(
        "/api/v2/homework/answers/",
        {
            "question": question.slug,
            "content": JSON,
        },
    )

    created = get_answer()

    assert created.parent is None
    assert created.question == question


def test_nonexistant_parent(api, question):
    api.post(
        "/api/v2/homework/answers/",
        {
            "parent": "41c24524-3d44-4cb8-ace3-c4cded405b24",  # не существует, инфа сотка
            "question": question.slug,
            "content": JSON,
        },
        expected_status_code=400,
    )


@pytest.mark.parametrize("empty_parent", ["", None])
def test_empty_parent(api, question, empty_parent):
    api.post(
        "/api/v2/homework/answers/",
        {
            "parent": empty_parent,
            "question": question.slug,
            "content": JSON,
        },
    )

    created = get_answer()

    assert created.parent is None


def test_create_answer_without_parent_do_not_have_parent_field_in_response(api, question):
    """Just to document weird behavior of our API: we hide the parent field when it is empty"""
    got = api.post(
        "/api/v2/homework/answers/",
        {
            "question": question.slug,
            "content": JSON,
        },
    )

    assert "parent" not in got


@pytest.mark.usefixtures("_no_purchase")
def test_404_for_not_purchased_users(api, question):
    api.post(
        "/api/v2/homework/answers/",
        {
            "question": question.slug,
            "content": JSON,
        },
        expected_status_code=404,
    )


@pytest.mark.usefixtures("_no_purchase")
def test_ok_for_users_that_purchased_another_course_from_the_same_group(api, question, course, factory):
    """Create a purchase of the item with the same group as the course, and check if user can post an answer"""
    another_course = factory.course(group=course.group)
    factory.order(item=another_course, user=api.user, is_paid=True)

    api.post(
        "/api/v2/homework/answers/",
        {
            "question": question.slug,
            "content": JSON,
        },
        expected_status_code=201,
    )


@pytest.mark.usefixtures("_no_purchase")
def test_parent_answer_ok_for_users_that_purchased_another_course_from_the_same_group(api, question, course, another_answer, factory):
    """Same as above, but for the non-root answer"""
    another_course = factory.course(group=course.group)
    factory.order(item=another_course, user=api.user, is_paid=True)

    api.post(
        "/api/v2/homework/answers/",
        {
            "question": question.slug,
            "parent": another_answer.slug,
            "content": JSON,
        },
        expected_status_code=201,
    )


@pytest.mark.usefixtures("_no_purchase")
@pytest.mark.parametrize(
    "permission",
    [
        "homework.see_all_questions",
        "studying.purchased_all_courses",
    ],
)
def test_ok_for_users_with_permission(api, question, permission):
    assert api.user.is_superuser is False
    api.user.add_perm(permission)

    api.post(
        "/api/v2/homework/answers/",
        {
            "question": question.slug,
            "content": JSON,
        },
        expected_status_code=201,
    )

    created = get_answer()

    assert created.author == api.user
    assert created.study is None


@pytest.mark.usefixtures("_no_purchase")
def test_ok_for_superusers(api, question):
    api.user.update(is_superuser=True)

    api.post(
        "/api/v2/homework/answers/",
        {
            "question": question.slug,
            "content": JSON,
        },
        expected_status_code=201,
    )

    created = get_answer()

    assert created.author == api.user
    assert created.study is None


def test_404_if_user_has_no_order_at_all(api, question, purchase):
    purchase.delete()

    api.post(
        "/api/v2/homework/answers/",
        {
            "content": JSON,
            "question": question.slug,
            "parent": None,
        },
        expected_status_code=404,
    )

    created = get_answer()
    assert created is None


@pytest.mark.freeze_time("2032-01-01 12:30Z")
def test_marks_crosscheck_as_checked(api, question, another_answer, mixer):
    crosscheck = mixer.blend("homework.AnswerCrossCheck", answer=another_answer, checker=api.user)

    api.post(
        "/api/v2/homework/answers/",
        {
            "content": JSON,
            "question": question.slug,
            "parent": another_answer.slug,
        },
    )

    crosscheck.refresh_from_db()
    assert crosscheck.checked == datetime(2032, 1, 1, 12, 30, tzinfo=timezone.utc)


def test_doesnt_marks_crosscheck_as_checked_for_another_answer(api, question, another_answer, mixer):
    crosscheck = mixer.blend("homework.AnswerCrossCheck", checker=api.user)

    api.post(
        "/api/v2/homework/answers/",
        {
            "content": JSON,
            "question": question.slug,
            "parent": another_answer.slug,
        },
    )

    crosscheck.refresh_from_db()
    assert crosscheck.checked is None


def test_doesnt_marks_crosscheck_as_checked_for_another_checker(api, question, another_answer, another_user, mixer):
    crosscheck = mixer.blend("homework.AnswerCrossCheck", answer=another_answer, checker=another_user)

    api.post(
        "/api/v2/homework/answers/",
        {
            "content": JSON,
            "question": question.slug,
            "parent": another_answer.slug,
        },
    )

    crosscheck.refresh_from_db()
    assert crosscheck.checked is None
