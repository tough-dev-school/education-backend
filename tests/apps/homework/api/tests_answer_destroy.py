from datetime import datetime, timezone

import pytest

from apps.homework.models import Answer

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time("2032-12-01 15:30"),
    pytest.mark.usefixtures("purchase"),
]


@pytest.fixture
def answer_of_another_author(mixer, question, another_user):
    return mixer.blend("homework.Answer", question=question, author=another_user)


def test_ok(api, answer):
    api.delete(f"/api/v2/homework/answers/{answer.slug}/")

    with pytest.raises(Answer.DoesNotExist):
        answer.refresh_from_db()


def test_destroy_non_root_answer(api, answer, answer_of_another_author):
    answer.update(parent=answer_of_another_author)

    api.delete(f"/api/v2/homework/answers/{answer.slug}/")

    with pytest.raises(Answer.DoesNotExist):
        answer.refresh_from_db()


@pytest.mark.usefixtures("child_answer")
def test_only_answers_without_descendants_may_be_destroyed(api, answer):
    Answer.objects.update(created="2032-12-01 15:30:12+03:00")

    api.delete(f"/api/v2/homework/answers/{answer.slug}/", expected_status_code=403)


def test_only_answers_not_longer_than_a_day_may_be_destroyed(api, answer, freezer):
    freezer.move_to("2032-12-02 15:30")

    api.delete(f"/api/v2/homework/answers/{answer.slug}/", expected_status_code=403)


def test_answers_created_within_a_day_may_be_destroyed(api, answer, freezer):
    freezer.move_to("2032-12-02 16:20+05:00")

    Answer.objects.update(created="2032-12-01 16:24+05:00")

    api.delete(f"/api/v2/homework/answers/{answer.slug}/", expected_status_code=204)


def test_can_not_destroy_answer_of_another_author(api, answer_of_another_author):
    api.user.add_perm("homework.answer.see_all_answers")

    api.delete(f"/api/v2/homework/answers/{answer_of_another_author.slug}/", expected_status_code=403)


def test_marks_crosscheck_as_unchecked(api, answer, child_answer_of_same_user, mixer):
    crosscheck = mixer.blend("homework.AnswerCrossCheck", answer=answer, checker=api.user, checked_at=datetime(2032, 1, 1, 12, 30, tzinfo=timezone.utc))

    api.delete(f"/api/v2/homework/answers/{child_answer_of_same_user.slug}/", expected_status_code=204)

    crosscheck.refresh_from_db()
    assert crosscheck.checked_at is None


def test_doesnt_mark_crosscheck_as_unchecked_if_removed_not_last_answer(api, answer, question, child_answer_of_same_user, mixer):
    mixer.blend("homework.Answer", question=question, parent=answer, author=api.user)
    crosscheck = mixer.blend("homework.AnswerCrossCheck", answer=answer, checker=api.user, checked_at=datetime(2032, 1, 1, 12, 30, tzinfo=timezone.utc))

    api.delete(f"/api/v2/homework/answers/{child_answer_of_same_user.slug}/", expected_status_code=204)

    crosscheck.refresh_from_db()
    assert crosscheck.checked_at == datetime(2032, 1, 1, 12, 30, tzinfo=timezone.utc)


def test_mark_crosscheck_as_unchecked_with_another_author_answers(api, answer, question, child_answer_of_same_user, mixer):
    mixer.blend("homework.Answer", question=question, parent=answer)
    crosscheck = mixer.blend("homework.AnswerCrossCheck", answer=answer, checker=api.user, checked_at=datetime(2032, 1, 1, 12, 30, tzinfo=timezone.utc))

    api.delete(f"/api/v2/homework/answers/{child_answer_of_same_user.slug}/", expected_status_code=204)

    crosscheck.refresh_from_db()
    assert crosscheck.checked_at is None


def test_doesnt_mark_crosscheck_as_checked_for_another_answer(api, child_answer_of_same_user, mixer):
    crosscheck = mixer.blend("homework.AnswerCrossCheck", checker=api.user, checked_at=datetime(2032, 1, 1, 12, 30, tzinfo=timezone.utc))

    api.delete(f"/api/v2/homework/answers/{child_answer_of_same_user.slug}/", expected_status_code=204)

    crosscheck.refresh_from_db()
    assert crosscheck.checked_at == datetime(2032, 1, 1, 12, 30, tzinfo=timezone.utc)


def test_doesnt_mark_crosscheck_as_checked_for_another_checker(api, answer, child_answer_of_same_user, mixer):
    crosscheck = mixer.blend("homework.AnswerCrossCheck", answer=answer, checked_at=datetime(2032, 1, 1, 12, 30, tzinfo=timezone.utc))

    api.delete(f"/api/v2/homework/answers/{child_answer_of_same_user.slug}/", expected_status_code=204)

    crosscheck.refresh_from_db()
    assert crosscheck.checked_at == datetime(2032, 1, 1, 12, 30, tzinfo=timezone.utc)
