import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("lesson", "answer"),
]


def test_no_sent_answers(api, module, answer):
    answer.delete()

    got = api.get(f"/api/v2/lms/lessons/?module={module.pk}")

    assert got["results"][0]["homework"]["is_sent"] is False


def test_answer_is_sent(api, module):
    got = api.get(f"/api/v2/lms/lessons/?module={module.pk}")

    assert got["results"][0]["homework"]["is_sent"] is True


def test_other_user_answers_are_ignored(another_user, api, module, answer):
    answer.update(author=another_user)

    got = api.get(f"/api/v2/lms/lessons/?module={module.pk}")

    assert got["results"][0]["homework"]["is_sent"] is False


def test_other_question_answers_are_ignored(another_question, api, module, answer):
    answer.update(question=another_question)

    got = api.get(f"/api/v2/lms/lessons/?module={module.pk}")

    assert got["results"][0]["homework"]["is_sent"] is False


def test_non_root_answer_are_ignored(api, mixer, module, question, another_user, answer):
    root_answer_of_another_user = mixer.blend("homework.Answer", author=another_user, question=question, parent=None)
    answer.update(parent=root_answer_of_another_user)

    got = api.get(f"/api/v2/lms/lessons/?module={module.pk}")

    assert got["results"][0]["homework"]["is_sent"] is False
