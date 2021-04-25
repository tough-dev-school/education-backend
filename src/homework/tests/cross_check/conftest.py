import pytest

from homework.services import AnswerCrossCheckDispatcher

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def dispatcher():
    return AnswerCrossCheckDispatcher


@pytest.fixture
def answers(mixer, user, another_user):
    return [
        mixer.blend('homework.Answer', author=user),
        mixer.blend('homework.Answer', author=another_user),
    ]
