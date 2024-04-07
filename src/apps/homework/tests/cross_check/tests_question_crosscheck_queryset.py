import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def another_question(mixer):
    return mixer.blend("homework.Question")


@pytest.fixture
def another_answer(mixer, question):
    return mixer.blend("homework.Answer", question=question)


def test_two_answers_by_default(question_dispatcher, answers):
    assert answers[0] in question_dispatcher.get_answers_to_check()
    assert answers[1] in question_dispatcher.get_answers_to_check()


def test_answers_with_exsclusion_flag_are_excluded(question_dispatcher, answers):
    answers[0].update(do_not_crosscheck=True)

    assert answers[0] not in question_dispatcher.get_answers_to_check()


def test_answers_from_another_questions_are_excluded(question_dispatcher, answers, another_question):
    answers[0].update(question=another_question)

    assert answers[0] not in question_dispatcher.get_answers_to_check()


def test_non_root_answers_are_excluded(question_dispatcher, answers, another_answer):
    answers[0].update(parent=another_answer)

    assert answers[0] not in question_dispatcher.get_answers_to_check()
