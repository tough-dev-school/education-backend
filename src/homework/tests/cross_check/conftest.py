import pytest

from homework.services import AnswerCrossCheckDispatcher

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def dispatcher():
    return AnswerCrossCheckDispatcher


@pytest.fixture
def answers(mixer):
    return mixer.cycle(2).blend('homework.Answer')
