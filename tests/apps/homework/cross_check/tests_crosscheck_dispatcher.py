import pytest

from apps.homework.models import AnswerCrossCheck

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def dispatcher(dispatcher, answers):
    return dispatcher(answers=answers, answers_per_user=1)


@pytest.mark.repeat(10)
def test_records_are_created(dispatcher, answers, user, another_user):
    dispatcher()

    assert AnswerCrossCheck.objects.filter(answer=answers[0]).exists()
    assert AnswerCrossCheck.objects.filter(answer=answers[1]).exists()

    assert AnswerCrossCheck.objects.filter(checker=user).exists()
    assert AnswerCrossCheck.objects.filter(checker=another_user).exists()


def test_records_are_returned(dispatcher):
    records = dispatcher()

    assert len(records) == 2
