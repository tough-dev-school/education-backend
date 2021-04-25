import pytest

pytestmark = [pytest.mark.django_db]


def get_crosscheck_count(user, dispatcher):
    user = dispatcher.get_users_with_cross_check_count().filter(id=user.pk).first()

    return user.crosscheck_count


def test_no_crosschecks(user, dispatcher, answers):
    dispatcher = dispatcher(answers=answers, users=[user])

    assert get_crosscheck_count(user, dispatcher) == 0


def test_no_crosschecks_from_non_dispatched_answers(mixer, user, dispatcher, answers):
    mixer.blend('homework.AnswerCrossCheck', answer=answers[0], checker=user)
    dispatcher = dispatcher(answers=answers[1:], users=[user])

    assert get_crosscheck_count(user, dispatcher) == 0


def test_no_crosschecks_from_other_answers(mixer, user, dispatcher, answers):
    mixer.blend('homework.AnswerCrossCheck', checker=user)
    dispatcher = dispatcher(answers=answers, users=[user])

    assert get_crosscheck_count(user, dispatcher) == 0


def test_no_crosschecks_from_other_users(mixer, user, dispatcher, answers):
    mixer.blend('homework.AnswerCrossCheck', answer=answers[1])
    dispatcher = dispatcher(answers=answers, users=[user])

    assert get_crosscheck_count(user, dispatcher) == 0


def test_single_cross_check(mixer, user, dispatcher, answers):
    mixer.blend('homework.AnswerCrossCheck', checker=user, answer=answers[1])
    dispatcher = dispatcher(answers=answers, users=[user])

    assert get_crosscheck_count(user, dispatcher) == 1
