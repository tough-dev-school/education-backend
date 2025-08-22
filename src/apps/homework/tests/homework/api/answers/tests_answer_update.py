from datetime import datetime, timedelta, timezone

import pytest

from apps.homework.models import Answer

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time("2032-12-01 15:30:12+03:00"),
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
                    "text": "Горите в аду (отредактировано в 08:30)",
                }
            ],
        }
    ],
}


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


def test_changing_text(api, answer):
    api.patch(f"/api/v2/homework/answers/{answer.slug}/", {"text": "*patched*"})

    answer.refresh_from_db()

    assert answer.text == "*patched*"
    assert answer.modified == datetime(2032, 12, 1, 15, 30, 12, tzinfo=timezone(timedelta(hours=3)))  # modified time updated


def test_changing_json(api, answer):
    api.patch(f"/api/v2/homework/answers/{answer.slug}/", {"content": JSON})

    answer.refresh_from_db()

    assert answer.content == JSON
    assert answer.modified == datetime(2032, 12, 1, 15, 30, 12, tzinfo=timezone(timedelta(hours=3)))  # modified time updated


def test_patch_changing_content_response_fields(api, answer, another_answer):
    got = api.patch(f"/api/v2/homework/answers/{answer.slug}/", {"content": JSON})

    assert got["created"] == "2032-12-01T15:30:12+03:00"
    assert got["modified"] == "2032-12-01T15:30:12+03:00"
    assert "-4" in got["slug"]
    assert got["question"] == str(answer.question.slug)
    assert got["parent"] == str(another_answer.slug)
    assert got["author"]["uuid"] == str(api.user.uuid)
    assert got["author"]["first_name"] == api.user.first_name
    assert got["author"]["last_name"] == api.user.last_name
    assert got["content"] == JSON
    assert got["has_descendants"] is False
    assert got["is_editable"] is True


def test_update_answer_without_parent_do_not_have_parent_field_in_response(api, answer):
    """Just to document weird behavior of our API: we hide the parent field when it is empty"""
    answer.update(parent=None)

    got = api.patch(f"/api/v2/homework/answers/{answer.slug}/", {"content": JSON})

    assert "parent" not in got


def test_405_for_put(api, answer):
    api.put(f"/api/v2/homework/answers/{answer.slug}/", {"content": JSON}, expected_status_code=405)


def test_only_answers_not_longer_than_a_day_may_be_edited(api, answer, freezer):
    freezer.move_to("2032-12-02 16:30+03:00")

    api.patch(f"/api/v2/homework/answers/{answer.slug}/", {"content": JSON}, expected_status_code=403)


def test_answers_created_within_a_day_may_be_updated(api, answer, freezer):
    freezer.move_to("2032-12-02 16:20+03:00")

    Answer.objects.update(created="2032-12-01 16:24+03:00")

    api.patch(f"/api/v2/homework/answers/{answer.slug}/", {"content": JSON}, expected_status_code=200)


@pytest.mark.usefixtures("child_answer")
def test_only_answers_without_descendants_may_be_edited(api, answer):
    Answer.objects.update(created="2032-12-01 15:30:12+03:00")

    api.patch(f"/api/v2/homework/answers/{answer.slug}/", {"content": JSON}, expected_status_code=403)


def test_404_for_answer_of_another_author(api, answer, another_user):
    answer.update(author=another_user)

    api.patch(f"/api/v2/homework/answers/{answer.slug}/", {"content": JSON}, expected_status_code=404)


def test_changing_text_response(api, answer):
    got = api.patch(f"/api/v2/homework/answers/{answer.slug}/", {"content": JSON})

    assert got["content"] == JSON
