from datetime import datetime, timezone

import pytest

from apps.homework.models import Answer

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("purchase"),
    pytest.mark.freeze_time("2032-01-01 12:30Z"),
]


@pytest.fixture
def _no_purchase(purchase):
    purchase.update(paid=None)


def get_answer():
    return Answer.objects.last()


def test_creation(api, question, another_answer):
    api.post(
        "/api/v2/homework/answers/",
        {
            "text": "Горите в аду!",
            "question": question.slug,
            "parent": another_answer.slug,
        },
    )

    created = get_answer()

    assert created.question == question
    assert created.parent == another_answer
    assert created.author == api.user
    assert created.text == "Горите в аду!"


@pytest.mark.usefixtures("kamchatka_timezone")
@pytest.mark.freeze_time("2023-01-23 08:30:40+12:00")
def test_create_answer_fields(api, question, another_answer):
    got = api.post(
        "/api/v2/homework/answers/",
        {
            "text": "Да ты умничка!",
            "question": question.slug,
            "parent": another_answer.slug,
        },
    )

    assert len(got) == 10
    assert got["created"] == "2023-01-23T08:30:40+12:00"
    assert got["modified"] == "2023-01-23T08:30:40+12:00"
    assert "-4" in got["slug"]
    assert got["question"] == str(question.slug)
    assert got["author"]["uuid"] == str(api.user.uuid)
    assert got["author"]["first_name"] == api.user.first_name
    assert got["author"]["last_name"] == api.user.last_name
    assert got["parent"] == str(another_answer.slug)
    assert got["text"] == "<p>Да ты умничка!</p>\n"
    assert got["src"] == "Да ты умничка!"
    assert got["has_descendants"] is False  # just created answer couldn't have descendants
    assert got["reactions"] == []  # just created answer couldn't have reactions


def test_without_parent(api, question):
    api.post(
        "/api/v2/homework/answers/",
        {
            "question": question.slug,
            "text": "Верните деньги!",
        },
    )

    created = get_answer()

    assert created.parent is None


def test_empty_parent(api, question):
    api.post(
        "/api/v2/homework/answers/",
        {
            "parent": None,
            "question": question.slug,
            "text": "Верните деньги!",
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
            "text": "Верните деньги!",
        },
    )

    assert len(got) == 9
    assert "parent" not in got


@pytest.mark.xfail(reason="WIP: will per-course permissions later")
@pytest.mark.usefixtures("_no_purchase")
def test_403_for_not_purchased_users(api, question):
    api.post(
        "/api/v2/homework/answers/",
        {
            "question": question.slug,
            "text": "Верните деньги!",
        },
        expected_status_code=403,
    )


@pytest.mark.usefixtures("_no_purchase")
def test_ok_for_users_with_permission(api, question):
    api.user.add_perm("homework.question.see_all_questions")

    api.post(
        "/api/v2/homework/answers/",
        {
            "question": question.slug,
            "text": "Верните деньги!",
        },
        expected_status_code=201,
    )


@pytest.mark.usefixtures("_no_purchase")
def test_ok_for_superusers(api, question):
    api.user.update(is_superuser=True)

    api.post(
        "/api/v2/homework/answers/",
        {
            "question": question.slug,
            "text": "Верните деньги!",
        },
        expected_status_code=201,
    )


@pytest.mark.xfail(strict=True, reason="Мы не проверяем право доступа к вопросу при создании ответа. Считаем это неважным, см #1370")
def test_403_if_user_has_not_purchase_record_at_all(api, question, purchase):
    purchase.delete()

    api.post(
        "/api/v2/homework/answers/",
        {
            "text": "Чёто права доступа не сделали",
            "question": question.slug,
            "parent": None,
        },
        expected_status_code=403,
    )

    created = get_answer()
    assert created is None


def test_marks_crosscheck_as_checked(api, question, another_answer, mixer):
    crosscheck = mixer.blend("homework.AnswerCrossCheck", answer=another_answer, checker=api.user)

    api.post(
        "/api/v2/homework/answers/",
        {
            "text": "Горите в аду!",
            "question": question.slug,
            "parent": another_answer.slug,
        },
    )

    crosscheck.refresh_from_db()
    assert crosscheck.checked_at == datetime(2032, 1, 1, 12, 30, tzinfo=timezone.utc)


def test_doesnt_marks_crosscheck_as_checked_for_another_answer(api, question, another_answer, mixer):
    crosscheck = mixer.blend("homework.AnswerCrossCheck", checker=api.user)

    api.post(
        "/api/v2/homework/answers/",
        {
            "text": "Горите в аду!",
            "question": question.slug,
            "parent": another_answer.slug,
        },
    )

    crosscheck.refresh_from_db()
    assert crosscheck.checked_at is None


def test_doesnt_marks_crosscheck_as_checked_for_another_checker(api, question, another_answer, ya_user, mixer):
    crosscheck = mixer.blend("homework.AnswerCrossCheck", answer=another_answer, checker=ya_user)

    api.post(
        "/api/v2/homework/answers/",
        {
            "text": "Горите в аду!",
            "question": question.slug,
            "parent": another_answer.slug,
        },
    )

    crosscheck.refresh_from_db()
    assert crosscheck.checked_at is None
