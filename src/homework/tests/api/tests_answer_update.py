from datetime import datetime
from datetime import timedelta
from datetime import timezone
import pytest

from homework.models import Answer

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time("2032-12-01 15:30:12+03:00"),
    pytest.mark.usefixtures("purchase"),
]


@pytest.fixture
def answer(answer, another_answer):
    Answer.objects.filter(pk=answer.pk).update(
        modified="2032-12-01 15:10+03:00",  # force to set modified time
        parent=another_answer,
    )

    answer.refresh_from_db()
    return answer


@pytest.fixture
def answer_of_another_author(mixer, question, another_user):
    return mixer.blend("homework.Answer", question=question, author=another_user)


def test_changing_text(api, answer):
    api.patch(f"/api/v2/homework/answers/{answer.slug}/", {"text": "*patched*"})

    answer.refresh_from_db()

    assert answer.text == "*patched*"
    assert answer.modified == datetime(2032, 12, 1, 15, 30, 12, tzinfo=timezone(timedelta(hours=3)))  # modified time updated


def test_patch_changing_text_response_fields(api, answer, another_answer):
    got = api.patch(f"/api/v2/homework/answers/{answer.slug}/", {"text": "*patched*"})

    assert len(got) == 10
    assert got["created"] == "2032-12-01T15:30:12+03:00"
    assert got["modified"] == "2032-12-01T15:30:12+03:00"
    assert "-4" in got["slug"]
    assert got["question"] == str(answer.question.slug)
    assert got["parent"] == str(another_answer.slug)
    assert got["author"]["uuid"] == str(api.user.uuid)
    assert got["author"]["first_name"] == api.user.first_name
    assert got["author"]["last_name"] == api.user.last_name
    assert got["text"] == "<p><em>patched</em></p>\n"
    assert got["src"] == "*patched*"
    assert got["has_descendants"] is False


def test_update_answer_without_parent_do_not_have_parent_field_in_response(api, question, answer):
    """Just to document weird behavior of our API: we hide the parent field when it is empty"""
    answer.parent = None
    answer.save()

    got = api.patch(f"/api/v2/homework/answers/{answer.slug}/", {"text": "*patched*"})

    assert len(got) == 9
    assert "parent" not in got


def test_405_for_put(api, answer):
    api.put(f"/api/v2/homework/answers/{answer.slug}/", {"text": "*patched*"}, expected_status_code=405)


def test_only_answers_not_longer_than_a_day_may_be_edited(api, answer, freezer):
    freezer.move_to("2032-12-02 16:30+03:00")

    api.patch(f"/api/v2/homework/answers/{answer.slug}/", {"text": "*patched*"}, expected_status_code=403)


def test_answers_created_within_a_day_may_be_updated(api, answer, freezer):
    freezer.move_to("2032-12-02 16:20+03:00")

    Answer.objects.update(created="2032-12-01 16:24+03:00")

    api.patch(f"/api/v2/homework/answers/{answer.slug}/", {"text": "*patched*"}, expected_status_code=200)


@pytest.mark.usefixtures("child_answer")
def test_only_answers_without_descendants_may_be_edited(api, answer):
    Answer.objects.update(created="2032-12-01 15:30:12+03:00")

    api.patch(f"/api/v2/homework/answers/{answer.slug}/", {"text": "*patched*"}, expected_status_code=403)


@pytest.mark.xfail(reason="WIP: will add per-course permissions later")
@pytest.mark.usefixtures("_no_purchase")
def test_403_without_a_purchase(api, answer):
    api.patch(f"/api/v2/homework/answers/{answer.slug}/", {"text": "*patched*"}, expected_status_code=403)


def test_404_for_answer_of_another_author(api, answer_of_another_author):
    api.patch(f"/api/v2/homework/answers/{answer_of_another_author.slug}/", {"text": "*patched*"}, expected_status_code=404)


def test_changing_text_response(api, answer):
    got = api.patch(f"/api/v2/homework/answers/{answer.slug}/", {"text": "*patched*"})

    assert got["src"] == "*patched*"
    assert "<em>patched</em>" in got["text"]
