import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("lesson"),
]


def test_no_question(api, course, lesson):
    lesson.update(question=None)

    got = api.get(f"/api/v2/lessons/?course={course.slug}")

    assert got["results"][0]["id"] == lesson.id
    assert got["results"][0]["homework"] is None


def test_no_sent_questions(api, course):
    got = api.get(f"/api/v2/lessons/?course={course.slug}")

    assert got["results"][0]["homework"]["is_sent"] is False


def test_question_is_sent(api, mixer, course, question):
    mixer.blend("homework.Answer", author=api.user, question=question, parent_id=None)

    got = api.get(f"/api/v2/lessons/?course={course.slug}")

    assert got["results"][0]["homework"]["is_sent"] is True


def test_other_user_answers_are_ignored(another_user, api, mixer, course, question):
    mixer.blend("homework.Answer", author=another_user, question=question, parent_id=None)

    got = api.get(f"/api/v2/lessons/?course={course.slug}")

    assert got["results"][0]["homework"]["is_sent"] is False


def test_other_question_answers_are_ignored(api, mixer, course, another_question):
    mixer.blend("homework.Answer", author=api.user, question=another_question, parent_id=None)

    got = api.get(f"/api/v2/lessons/?course={course.slug}")

    assert got["results"][0]["homework"]["is_sent"] is False


def test_non_root_answer_are_ignored(api, mixer, course, question, another_user):
    root_answer_of_another_user = mixer.blend("homework.Answer", author=another_user, question=question, parent=None)
    mixer.blend("homework.Answer", author=api.user, question=question, parent=root_answer_of_another_user)

    got = api.get(f"/api/v2/lessons/?course={course.slug}")

    assert got["results"][0]["homework"]["is_sent"] is False
