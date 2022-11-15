import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures('purchase'),
]


@pytest.fixture
def answer_from_another_user(another_user, another_answer):
    another_answer.author = another_user
    another_answer.save()

    return another_answer


@pytest.mark.freeze_time('2022-10-09 10:30:12Z')
def test_ok(api, question, answer):
    got = api.get(f'/api/v2/homework/answers/?question={question.slug}')['results']

    assert got[0]['created'] == '2022-10-09T13:30:12+03:00'  # +3 hours default timezone
    assert got[0]['modified'] == '2022-10-09T13:30:12+03:00'  # +3 hours default timezone
    assert got[0]['slug'] == str(answer.slug)
    assert '<em>test</em>' in got[0]['text']
    assert got[0]['src'] == '*test*'
    assert got[0]['author']['uuid'] == str(api.user.uuid)
    assert got[0]['author']['first_name'] == api.user.first_name
    assert got[0]['author']['last_name'] == api.user.last_name


@pytest.mark.usefixtures('answer')
def test_answers_from_other_questions_are_excluded(api, another_question):
    got = api.get(f'/api/v2/homework/answers/?question={another_question.slug}')['results']

    assert len(got) == 0


def test_non_root_answers_are_excluded(api, question, answer, answer_from_another_user):
    answer.parent = answer_from_another_user
    answer.save()

    got = api.get(f'/api/v2/homework/answers/?question={question.slug}')['results']

    assert len(got) == 1  # only answer_from_another_user
    assert got[0]['slug'] == str(answer_from_another_user.slug)


@pytest.mark.usefixtures('answer', 'answer_from_another_user')
def test_answers_from_other_questions_are_excluded_even_if_user_has_the_permission(api, another_question):
    api.user.add_perm('homework.answer.see_all_answers')

    got = api.get(f'/api/v2/homework/answers/?question={another_question.slug}')['results']

    assert len(got) == 0


@pytest.mark.usefixtures('answer_from_another_user')
def test_answers_from_another_authors_are_excluded(api, question):
    got = api.get(f'/api/v2/homework/answers/?question={question.slug}')['results']

    assert len(got) == 0


def test_answers_from_another_authors_are_included_if_already_seen(api, mixer, question, answer_from_another_user):
    mixer.blend('homework.AnswerAccessLogEntry', user=api.user, answer=answer_from_another_user)

    got = api.get(f'/api/v2/homework/answers/?question={question.slug}')['results']

    assert len(got) == 1


def test_answers_from_another_authors_are_excluded_if_author_is_filtered(api, mixer, question, answer_from_another_user):
    mixer.blend('homework.AnswerAccessLogEntry', user=api.user, answer=answer_from_another_user)

    got = api.get(f'/api/v2/homework/answers/?question={question.slug}&author={api.user.uuid}')['results']

    assert len(got) == 0


def test_access_log_entries_from_another_users_do_not_break_the_select(api, mixer, question, answer):
    mixer.cycle(5).blend('homework.AnswerAccessLogEntry', question=question, answer=answer)

    got = api.get(f'/api/v2/homework/answers/?question={question.slug}')['results']

    assert len(got) == 1


@pytest.mark.usefixtures('answer_from_another_user')
def test_users_with_permission_may_see_all_answers(api, question):
    api.user.add_perm('homework.answer.see_all_answers')

    got = api.get(f'/api/v2/homework/answers/?question={question.slug}')['results']

    assert len(got) == 1


def test_no_anon(anon, question):
    anon.get(f'/api/v2/homework/answers/?question={question.slug}', expected_status_code=401)
