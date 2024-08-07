import pytest

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
def answer(mixer, user):
    return mixer.blend("homework.Answer", author=user)


@pytest.fixture
def child_answer(mixer, answer, ya_user):
    return mixer.blend("homework.Answer", parent=answer, author=ya_user)


def test_for_root_answer(answer, user):
    assert answer.is_author_of_root_answer(user) is True


def test_for_child_answer(child_answer, user):
    assert child_answer.is_author_of_root_answer(user) is True


def test_for_another_user_answer(answer, child_answer, ya_user):
    assert answer.is_author_of_root_answer(ya_user) is False
    assert child_answer.is_author_of_root_answer(ya_user) is False
