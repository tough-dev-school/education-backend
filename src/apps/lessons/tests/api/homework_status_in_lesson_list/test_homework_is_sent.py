import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("lesson"),
]


def test_no_sent_questions(api, module):
    got = api.get(f"/api/v2/lessons/?module={module.pk}")

    assert got["results"][0]["homework"]["is_sent"] is False


def test_question_is_sent(api, mixer, module, question):
    mixer.blend("homework.Answer", author=api.user, question=question, parent_id=None)

    got = api.get(f"/api/v2/lessons/?module={module.pk}")

    assert got["results"][0]["homework"]["is_sent"] is True


def test_other_user_answers_are_ignored(another_user, api, mixer, module, question):
    mixer.blend("homework.Answer", author=another_user, question=question, parent_id=None)

    got = api.get(f"/api/v2/lessons/?module={module.pk}")

    assert got["results"][0]["homework"]["is_sent"] is False


def test_other_question_answers_are_ignored(api, mixer, module, another_question):
    mixer.blend("homework.Answer", author=api.user, question=another_question, parent_id=None)

    got = api.get(f"/api/v2/lessons/?module={module.pk}")

    assert got["results"][0]["homework"]["is_sent"] is False


def test_non_root_answer_are_ignored(api, mixer, module, question, another_user):
    root_answer_of_another_user = mixer.blend("homework.Answer", author=another_user, question=question, parent=None)
    mixer.blend("homework.Answer", author=api.user, question=question, parent=root_answer_of_another_user)

    got = api.get(f"/api/v2/lessons/?module={module.pk}")

    assert got["results"][0]["homework"]["is_sent"] is False
