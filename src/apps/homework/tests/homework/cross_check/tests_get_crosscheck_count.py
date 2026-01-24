import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("_set_current_user"),
]


def get_crosscheck_count(answer, dispatcher):
    answer = dispatcher.get_answers_with_crosscheck_count().filter(id=answer.pk).first()

    return answer.crosscheck_count


def test_no_crosschecks(answer_dispatcher, answers):
    dispatcher = answer_dispatcher(answers=answers)

    assert get_crosscheck_count(answers[0], dispatcher) == 0


def test_no_crosschecks_from_non_dispatched_users(answer_dispatcher, mixer, answers):
    mixer.blend("homework.AnswerCrossCheck", answer=answers[1])
    dispatcher = answer_dispatcher(answers)

    assert get_crosscheck_count(answers[1], dispatcher) == 0


def test_crosschecks(answer_dispatcher, mixer, answers):
    mixer.blend("homework.AnswerCrossCheck", answer=answers[1], checker=answers[0].author)
    dispatcher = answer_dispatcher(answers)

    assert get_crosscheck_count(answers[1], dispatcher) == 1
