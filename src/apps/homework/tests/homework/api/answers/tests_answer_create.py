from datetime import datetime, timezone

import pytest

from apps.homework.models import Answer, AnswerCrossCheck

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("purchase"),
]


@pytest.fixture
def _no_purchase(purchase):
    purchase.unship()


def get_answer():
    return Answer.objects.last()


def test_creation_with_json(api, factory, question, another_answer, purchase):
    """Drop it when you remove the 'text' field"""
    api.post(
        "/api/v2/homework/answers/",
        {
            "content": factory.prosemirror("Горите в аду"),
            "question": question.slug,
            "parent": another_answer.slug,
        },
    )

    created = get_answer()

    assert created.question == question
    assert created.parent == another_answer
    assert created.author == api.user
    assert created.study == purchase.study
    assert created.content["content"][0]["content"][0]["text"] == "Горите в аду"
    assert created.legacy_text == "Горите в аду"


def test_no_json(api, question, another_answer):
    api.post(
        "/api/v2/homework/answers/",
        {
            "question": question.slug,
            "parent": another_answer.slug,
        },
        expected_status_code=400,
    )


def test_non_prosemirror_json(api, question, another_answer):
    api.post(
        "/api/v2/homework/answers/",
        {
            "content": {"invalid": "json"},
            "question": question.slug,
            "parent": another_answer.slug,
        },
        expected_status_code=400,
    )


def test_no_question(api, factory, another_answer):
    api.post(
        "/api/v2/homework/answers/",
        {
            "content": factory.prosemirror("Горите в аду"),
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
def test_create_answer_fields(api, factory, question, another_answer):
    got = api.post(
        "/api/v2/homework/answers/",
        {
            "content": factory.prosemirror("Горите в аду"),
            "question": question.slug,
            "parent": another_answer.slug,
        },
    )

    assert got["created"] == "2023-01-23T08:30:40+12:00"
    assert got["modified"] is None
    assert "-4" in got["slug"]
    assert got["question"] == str(question.slug)
    assert got["author"]["uuid"] == str(api.user.uuid)
    assert got["author"]["first_name"] == api.user.first_name
    assert got["author"]["last_name"] == api.user.last_name
    assert got["parent"] == str(another_answer.slug)
    assert got["content"] == factory.prosemirror("Горите в аду")
    assert got["has_descendants"] is False  # newly created answer couldn't have descendants
    assert got["is_editable"] is True  # and should be editable
    assert got["reactions"] == []  # and couldn't have reactions


def test_creating_root_answer(api, factory, question):
    api.post(
        "/api/v2/homework/answers/",
        {
            "question": question.slug,
            "content": factory.prosemirror("Горите в аду"),
        },
    )

    created = get_answer()

    assert created.parent is None
    assert created.question == question


def test_nonexistant_parent(api, factory, question):
    api.post(
        "/api/v2/homework/answers/",
        {
            "parent": "41c24524-3d44-4cb8-ace3-c4cded405b24",  # не существует, инфа сотка
            "question": question.slug,
            "content": factory.prosemirror("Горите в аду"),
        },
        expected_status_code=400,
    )


@pytest.mark.parametrize("empty_parent", ["", None])
def test_empty_parent(api, factory, question, empty_parent):
    api.post(
        "/api/v2/homework/answers/",
        {
            "parent": empty_parent,
            "question": question.slug,
            "content": factory.prosemirror("Горите в аду"),
        },
    )

    created = get_answer()

    assert created.parent is None


def test_create_answer_without_parent_do_not_have_parent_field_in_response(api, factory, question):
    """Just to document weird behavior of our API: we hide the parent field when it is empty"""
    got = api.post(
        "/api/v2/homework/answers/",
        {
            "question": question.slug,
            "content": factory.prosemirror("Горите в аду"),
        },
    )

    assert "parent" not in got


@pytest.mark.usefixtures("_no_purchase")
def test_404_for_not_purchased_users(api, factory, question):
    api.post(
        "/api/v2/homework/answers/",
        {
            "question": question.slug,
            "content": factory.prosemirror("Горите в аду"),
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
            "content": factory.prosemirror("Горите в аду"),
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
            "content": factory.prosemirror("Горите в аду"),
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
def test_ok_for_users_with_permission(api, factory, question, permission):
    assert api.user.is_superuser is False
    api.user.add_perm(permission)

    api.post(
        "/api/v2/homework/answers/",
        {
            "question": question.slug,
            "content": factory.prosemirror("Горите в аду"),
        },
        expected_status_code=201,
    )

    created = get_answer()

    assert created.author == api.user
    assert created.study is None


@pytest.mark.usefixtures("_no_purchase")
def test_ok_for_superusers(api, factory, question):
    api.user.update(is_superuser=True)

    api.post(
        "/api/v2/homework/answers/",
        {
            "question": question.slug,
            "content": factory.prosemirror("Горите в аду"),
        },
        expected_status_code=201,
    )

    created = get_answer()

    assert created.author == api.user
    assert created.study is None


def test_404_if_user_has_no_order_at_all(api, factory, question, purchase):
    purchase.delete()

    api.post(
        "/api/v2/homework/answers/",
        {
            "content": factory.prosemirror("Горите в аду"),
            "question": question.slug,
            "parent": None,
        },
        expected_status_code=404,
    )

    created = get_answer()
    assert created is None


@pytest.mark.freeze_time("2032-01-01 12:30Z")
def test_marks_crosscheck_as_checked(api, factory, question, another_answer, mixer):
    crosscheck = mixer.blend("homework.AnswerCrossCheck", answer=another_answer, checker=api.user)

    api.post(
        "/api/v2/homework/answers/",
        {
            "content": factory.prosemirror("Горите в аду"),
            "question": question.slug,
            "parent": another_answer.slug,
        },
    )

    crosscheck.refresh_from_db()
    assert crosscheck.checked == datetime(2032, 1, 1, 12, 30, tzinfo=timezone.utc)


def test_doesnt_marks_crosscheck_as_checked_for_another_answer(api, factory, question, another_answer, mixer):
    crosscheck = mixer.blend("homework.AnswerCrossCheck", checker=api.user)

    api.post(
        "/api/v2/homework/answers/",
        {
            "content": factory.prosemirror("Горите в аду"),
            "question": question.slug,
            "parent": another_answer.slug,
        },
    )

    crosscheck.refresh_from_db()
    assert crosscheck.checked is None


def test_does_not_mark_crosscheck_as_checked_for_another_checker(api, factory, question, another_answer, another_user, mixer):
    crosscheck = mixer.blend("homework.AnswerCrossCheck", answer=another_answer, checker=another_user)

    api.post(
        "/api/v2/homework/answers/",
        {
            "content": factory.prosemirror("Горите в аду"),
            "question": question.slug,
            "parent": another_answer.slug,
        },
    )

    crosscheck.refresh_from_db()
    assert crosscheck.checked is None


def test_crosscheck_is_created_automaticaly_if_there_were_not(api, factory, question, another_user, mixer):
    answer_from_another_user = mixer.blend("homework.Answer", question=question, author=another_user)

    api.post(
        "/api/v2/homework/answers/",
        {
            "content": factory.prosemirror("Горите в аду"),
            "question": question.slug,
            "parent": answer_from_another_user.slug,
        },
    )

    automaticaly_created_crosscheck = AnswerCrossCheck.objects.get(answer=answer_from_another_user, checker=api.user)

    assert automaticaly_created_crosscheck.checked is not None


def test_crosscheck_is_not_created_when_replying_to_own_answer(api, factory, question, another_answer):
    api.post(
        "/api/v2/homework/answers/",
        {
            "content": factory.prosemirror("Горите в аду"),
            "question": question.slug,
            "parent": another_answer.slug,
        },
    )

    assert not AnswerCrossCheck.objects.filter(answer=another_answer, checker=api.user).exists()


def test_crosscheck_is_not_created_when_replying_to_non_root_answer(api, factory, question, another_user, mixer):
    root_answer = mixer.blend("homework.Answer", question=question, parent=None)
    answer_from_another_user = mixer.blend("homework.Answer", question=question, author=another_user, parent=root_answer)

    api.post(
        "/api/v2/homework/answers/",
        {
            "content": factory.prosemirror("Горите в аду"),
            "question": question.slug,
            "parent": answer_from_another_user.slug,
        },
    )

    assert not AnswerCrossCheck.objects.filter(answer=answer_from_another_user, checker=api.user).exists()
