import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures('purchase'),
]


@pytest.fixture
def api(api):
    api.user.is_superuser = False
    api.user.save()

    return api


@pytest.fixture
def another_user(mixer):
    return mixer.blend('users.User')


def test_ok(api, question, answer):
    got = api.get(f'/api/v2/homework/questions/{question.slug}/answers/')['results']

    assert got[0]['slug'] == str(answer.slug)
    assert got[0]['author']['first_name'] == api.user.first_name
    assert got[0]['author']['last_name'] == api.user.last_name


def test_answers_from_another_authors_are_excluded(api, question, answer, another_user):
    answer.author = another_user
    answer.save()

    got = api.get(f'/api/v2/homework/questions/{question.slug}/answers/')['results']

    assert len(got) == 0


def test_users_with_permission_may_see_all_answers(api, question, answer, another_user):
    answer.author = another_user
    answer.save()
    api.user.add_perm('homework.answer.see_all_answers')

    got = api.get(f'/api/v2/homework/questions/{question.slug}/answers/')['results']

    assert len(got) == 1


def test_child_answers_from_another_authors_are_included(api, mixer, question, answer, another_user):
    another_answer = mixer.blend('homework.Answer', author=another_user, parent=answer)

    got = api.get(f'/api/v2/homework/questions/{question.slug}/answers/')['results']

    assert len(got) == 2
    assert got[1]['slug'] == str(another_answer.slug)
