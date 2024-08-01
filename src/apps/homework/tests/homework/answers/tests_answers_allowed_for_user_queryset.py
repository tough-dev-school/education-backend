import pytest

from apps.homework.models import Answer

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def root_answer(mixer, user):
    return mixer.blend("homework.Answer", author=user)


@pytest.fixture
def answer_one(mixer, user):
    return mixer.blend("homework.Answer", author=user)


@pytest.fixture
def answer_two(mixer, user):
    return mixer.blend("homework.Answer", author=user)


@pytest.fixture
def child_of_answer_two(mixer, answer_two):
    return mixer.blend("homework.Answer", parent=answer_two)


@pytest.fixture
def answer_access_log_entry(mixer, user, answer_one):
    return mixer.blend("homework.AnswerAccessLogEntry", answer=answer_one, user=user)


def answers(user):
    return Answer.objects.allowed_for_user(user)


def test_personal_root_answers_are_included(answer_one, answer_two, user):
    assert answer_one in answers(user)
    assert answer_two in answers(user)


def test_other_authors_are_excluded(answer_one, another_user, user):
    answer_one.update(author=another_user)

    assert answer_one not in answers(user)


def test_other_answers_included_for_user_with_see_all_answers_permissions(answer_one, user, another_user):
    answer_one.update(author=another_user)
    user.add_perm("homework.answer.see_all_answers")

    assert answer_one in answers(user)


@pytest.mark.usefixtures("answer_access_log_entry")
def test_other_authors_are_included_if_seen(answer_one, another_user, user):
    answer_one.update(author=another_user)

    assert answer_one in answers(user)


@pytest.mark.usefixtures("answer_access_log_entry")
def test_no_weird_orm_quirks_on_answers_accessed_by_multiple_users(mixer, answer_one, another_user, user):
    mixer.cycle(5).blend("homework.AnswerAccessLogEntry", answer=answer_one)

    answer_one.update(author=another_user)

    assert answers(user).count() == 1


def test_child_answers_from_another_users_are_included(answer_one, answer_two, another_user, user):
    answer_two.update(author=another_user, parent=answer_one)

    assert answer_one in answers(user)
    assert answer_two in answers(user)


def test_sibling_answers_are_included(answer_one, answer_two, root_answer, user, another_user):
    answer_one.update(parent=root_answer)
    answer_two.update(author=another_user, parent=root_answer)

    assert answer_one in answers(user)
    assert answer_two in answers(user)


def test_children_of_sibling_answers_are_included(answer_one, answer_two, root_answer, user, another_user, child_of_answer_two):
    answer_one.update(parent=root_answer)
    answer_two.update(author=another_user, parent=root_answer)

    assert child_of_answer_two in answers(user)
