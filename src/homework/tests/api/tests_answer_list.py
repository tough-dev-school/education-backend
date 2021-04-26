import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures('purchase'),
]


@pytest.fixture
def another_user(mixer):
    return mixer.blend('users.User')


@pytest.fixture
def answer_from_another_user(another_user, another_answer):
    another_answer.author = another_user
    another_answer.save()

    return another_answer


def test_ok(api, question, answer):
    got = api.get(f'/api/v2/homework/questions/{question.slug}/answers/')['results']

    assert 'created' in got[0]
    assert got[0]['slug'] == str(answer.slug)
    assert got[0]['author']['first_name'] == api.user.first_name
    assert got[0]['author']['last_name'] == api.user.last_name


@pytest.mark.usefixtures('answer')
def test_answers_from_other_questions_are_excluded(api, another_question):
    got = api.get(f'/api/v2/homework/questions/{another_question.slug}/answers/')['results']

    assert len(got) == 0


@pytest.mark.usefixtures('answer', 'answer_from_another_user')
def test_answers_from_other_questions_are_excluded_even_if_user_has_the_permission(api, another_question):
    api.user.add_perm('homework.answer.see_all_answers')

    got = api.get(f'/api/v2/homework/questions/{another_question.slug}/answers/')['results']

    assert len(got) == 0


@pytest.mark.usefixtures('answer_from_another_user')
def test_answers_from_another_authors_are_excluded(api, question):
    got = api.get(f'/api/v2/homework/questions/{question.slug}/answers/')['results']

    assert len(got) == 0


def test_answers_from_another_authors_are_included_if_already_seen(api, mixer, question, answer_from_another_user):
    mixer.blend('homework.AnswerAccessLogEntry', user=api.user, answer=answer_from_another_user)

    got = api.get(f'/api/v2/homework/questions/{question.slug}/answers/')['results']

    assert len(got) == 1


@pytest.mark.usefixtures('answer_from_another_user')
def test_users_with_permission_may_see_all_answers(api, question):
    api.user.add_perm('homework.answer.see_all_answers')

    got = api.get(f'/api/v2/homework/questions/{question.slug}/answers/')['results']

    assert len(got) == 1


def test_child_answers_from_another_authors_are_included(api, mixer, question, answer, answer_from_another_user):
    answer_from_another_user.parent = answer
    answer_from_another_user.save()

    got = api.get(f'/api/v2/homework/questions/{question.slug}/answers/')['results']

    assert len(got) == 2
    assert got[1]['slug'] == str(answer_from_another_user.slug)
