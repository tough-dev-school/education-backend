from datetime import datetime, timedelta, timezone

import pytest
from django.contrib.admin.models import CHANGE, LogEntry
from django.contrib.contenttypes.models import ContentType

from apps.homework.models import Answer

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time("2032-12-01 15:30:12+03:00"),
    pytest.mark.usefixtures("purchase"),
]


@pytest.fixture
def updated(factory):
    return factory.prosemirror("Горите в аду (отредактировано в 08:30)")


@pytest.fixture(autouse=True)
def _set_editability_period(settings):
    settings.HOMEWORK_ANSWER_EDIT_PERIOD = timedelta(days=1)


@pytest.fixture
def answer(answer, another_answer):
    Answer.objects.filter(pk=answer.pk).update(
        modified="2032-12-01 15:10+03:00",  # force to set modified time
        parent=another_answer,
    )

    answer.refresh_from_db()
    return answer


def test_changing_json(api, updated, answer):
    api.patch(f"/api/v2/homework/answers/{answer.slug}/", {"content": updated})

    answer.refresh_from_db()

    assert answer.content == updated
    assert answer.legacy_text == "Горите в аду (отредактировано в 08:30)"
    assert answer.modified == datetime(2032, 12, 1, 15, 30, 12, tzinfo=timezone(timedelta(hours=3)))  # modified time updated


@pytest.mark.auditlog
@pytest.mark.usefixtures("_set_current_user")
def test_auditlog(api, updated, answer):
    api.patch(f"/api/v2/homework/answers/{answer.slug}/", {"content": updated})

    log = LogEntry.objects.filter(
        content_type=ContentType.objects.get_for_model(answer).id,
    ).last()

    assert log.action_flag == CHANGE
    assert log.user == api.user
    assert log.object_id == str(answer.id)

    assert "Answer content updated" in log.change_message
    assert "Пыщ" in log.change_message, "Previous content is saved"
    assert "в аду" in log.change_message, "New content is saved"


def test_no_json(api, answer):
    api.patch(f"/api/v2/homework/answers/{answer.slug}/", {}, expected_status_code=400)


def test_non_updated(api, answer):
    api.patch(f"/api/v2/homework/answers/{answer.slug}/", {"content": {"non": "prosemirror"}}, expected_status_code=400)


@pytest.mark.parametrize(
    "shit",
    [
        "",
        "text",
        ["a"],
        '{"a": "b"}',
    ],
)
def test_invalid_json(api, answer, shit):
    api.patch(
        f"/api/v2/homework/answers/{answer.slug}/",
        {"content": shit},
        expected_status_code=400,
    )


def test_patch_changing_content_response_fields(api, updated, answer, another_answer):
    got = api.patch(f"/api/v2/homework/answers/{answer.slug}/", {"content": updated})

    assert got["created"] == "2032-12-01T15:30:12+03:00"
    assert got["modified"] == "2032-12-01T15:30:12+03:00"
    assert "-4" in got["slug"]
    assert got["question"] == str(answer.question.slug)
    assert got["parent"] == str(another_answer.slug)
    assert got["author"]["uuid"] == str(api.user.uuid)
    assert got["author"]["first_name"] == api.user.first_name
    assert got["author"]["last_name"] == api.user.last_name
    assert got["content"] == updated
    assert got["has_descendants"] is False
    assert got["is_editable"] is True


def test_update_answer_without_parent_do_not_have_parent_field_in_response(api, updated, answer):
    """Just to document weird behavior of our API: we hide the parent field when it is empty"""
    answer.update(parent=None)

    got = api.patch(f"/api/v2/homework/answers/{answer.slug}/", {"content": updated})

    assert "parent" not in got


def test_405_for_put(api, updated, answer):
    api.put(f"/api/v2/homework/answers/{answer.slug}/", {"content": updated}, expected_status_code=405)


def test_only_answers_not_longer_than_a_day_may_be_edited(api, updated, answer, freezer):
    freezer.move_to("2032-12-02 16:30+03:00")

    api.patch(f"/api/v2/homework/answers/{answer.slug}/", {"content": updated}, expected_status_code=403)


def test_answers_created_within_a_day_may_be_updated(api, updated, answer, freezer):
    freezer.move_to("2032-12-02 16:20+03:00")

    Answer.objects.update(created="2032-12-01 16:24+03:00")

    api.patch(f"/api/v2/homework/answers/{answer.slug}/", {"content": updated}, expected_status_code=200)


@pytest.mark.usefixtures("child_answer")
def test_only_answers_without_descendants_may_be_edited(api, updated, answer):
    Answer.objects.update(created="2032-12-01 15:30:12+03:00")

    api.patch(f"/api/v2/homework/answers/{answer.slug}/", {"content": updated}, expected_status_code=403)


def test_404_for_answer_of_another_author(api, updated, answer, another_user):
    answer.update(author=another_user)

    api.patch(f"/api/v2/homework/answers/{answer.slug}/", {"content": updated}, expected_status_code=404)


def test_response(api, updated, answer):
    got = api.patch(f"/api/v2/homework/answers/{answer.slug}/", {"content": updated})

    assert got["content"] == updated
