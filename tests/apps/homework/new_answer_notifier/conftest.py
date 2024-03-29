import pytest

from apps.homework.services import NewAnswerNotifier


@pytest.fixture
def notifier():
    return NewAnswerNotifier


@pytest.fixture
def another_answer(mixer):
    return mixer.blend("homework.Answer")


@pytest.fixture
def parent_of_another_answer(mixer, another_answer):
    answer = mixer.blend("homework.Answer")

    another_answer.update(parent=answer)

    return answer
