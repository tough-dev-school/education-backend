import pytest

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def question(mixer):
    return mixer.blend("homework.Question")


@pytest.fixture
def answer(mixer, question):
    return mixer.blend("homework.Answer", question=question)


@pytest.fixture
def child_answer(mixer, answer, question):
    return mixer.blend("homework.Answer", parent=answer, question=question)


def test_for_root_answer(answer):
    assert answer.is_root is True


def test_for_child_answer(child_answer):
    assert child_answer.is_root is False
