from typing import Callable

import pytest

from apps.homework.services.cross_check_task_processor import CrossCheckTaskProcessor

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def user(mixer):
    return mixer.blend("users.User")


@pytest.fixture
def ya_user(mixer):
    return mixer.blend("users.User")


@pytest.fixture
def question(mixer):
    return mixer.blend("homework.Question")


@pytest.fixture
def answer(mixer, question, user):
    return mixer.blend("homework.Answer", question=question, author=user)


@pytest.fixture
def ya_answer(mixer, question, ya_user):
    return mixer.blend("homework.Answer", question=question, author=ya_user)


@pytest.fixture
def crosscheck(mixer, user, ya_answer):
    return mixer.blend("homework.AnswerCrossCheck", checker=user, answer=ya_answer)


@pytest.fixture
def ya_crosscheck(mixer, ya_user, answer):
    return mixer.blend("homework.AnswerCrossCheck", checker=ya_user, answer=answer)


@pytest.fixture
def answer_on_ya_answer(mixer, question, ya_answer, user):
    return mixer.blend("homework.Answer", question=question, parent=ya_answer, author=user)


@pytest.fixture
def ya_answer_on_answer(mixer, question, answer, ya_user):
    return mixer.blend("homework.Answer", question=question, parent=answer, author=ya_user)


@pytest.fixture
def processor() -> "Callable":
    return lambda answer: CrossCheckTaskProcessor(answer)
