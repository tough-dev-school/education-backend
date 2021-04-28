import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures('purchase'),
]


@pytest.fixture
def another_answer(another_answer, answer, even_another_user):
    another_answer.parent = answer
    another_answer.author = even_another_user
    another_answer.save()

    return another_answer


@pytest.fixture
def child_of_another_answer(mixer, question, another_answer, another_user, api):
    return mixer.blend(
        'homework.Answer',
        question=question,
        author=another_user,
        parent=another_answer,
    )


@pytest.fixture
def even_another_user(mixer):
    return mixer.blend('users.User')


@pytest.fixture
def _very_huge_tree_of_answers(answer, mixer):
    previous_answer = answer
    for _ in range(0, 100):
        previous_answer = mixer.blend(
            'homework.Answer',
            question=previous_answer.question,
            parent=previous_answer,
            author=previous_answer.author,
        )


def test_no_descendants_by_default(api, answer):
    got = api.get(f'/api/v2/homework/answers/{answer.slug}/')

    assert got['descendants'] == []


def test_child_answers(api, answer, another_answer):
    got = api.get(f'/api/v2/homework/answers/{answer.slug}/')

    assert got['descendants'][0]['slug'] == str(another_answer.slug)
    assert got['descendants'][0]['author']['first_name'] == another_answer.author.first_name
    assert got['descendants'][0]['author']['last_name'] == another_answer.author.last_name


def test_multilevel_child_answers(api, answer, another_answer, child_of_another_answer):
    child_of_another_answer.author = api.user  # make child_of_another_answer accessible
    child_of_another_answer.save()

    got = api.get(f'/api/v2/homework/answers/{answer.slug}/')

    assert got['descendants'][0]['slug'] == str(another_answer.slug)
    assert got['descendants'][0]['descendants'][0]['slug'] == str(child_of_another_answer.slug)
    assert got['descendants'][0]['descendants'][0]['descendants'] == []


@pytest.mark.usefixtures('child_of_another_answer')
def test_only_immediate_siblings_are_included(api, answer):
    got = api.get(f'/api/v2/homework/answers/{answer.slug}/')

    assert len(got['descendants']) == 1


@pytest.mark.usefixtures('child_of_another_answer')
def test_descendants_from_another_author_are_not_accessable(api, answer):
    got = api.get(f'/api/v2/homework/answers/{answer.slug}/')

    assert len(got['descendants'][0]['descendants']) == 0


def test_descendants_from_another_author_are_accessable_if_accees_record_is_present(api, answer, child_of_another_answer, mixer):
    mixer.blend('homework.AnswerAccessLogEntry', user=api.user, answer=child_of_another_answer)

    got = api.get(f'/api/v2/homework/answers/{answer.slug}/')

    assert len(got['descendants'][0]['descendants']) == 1


@pytest.mark.usefixtures('child_of_another_answer')
def test_descendants_from_another_author_are_accessable_if_user_has_permission(api, answer):
    api.user.add_perm('homework.answer.see_all_answers')

    got = api.get(f'/api/v2/homework/answers/{answer.slug}/')

    assert len(got['descendants'][0]['descendants']) == 1


@pytest.mark.usefixtures('child_of_another_answer')
def test_descendants_from_another_author_are_accessable_if_user_is_superuser(api, answer):
    api.user.is_superuser = True
    api.user.save()

    got = api.get(f'/api/v2/homework/answers/{answer.slug}/')

    assert len(got['descendants'][0]['descendants']) == 1


@pytest.mark.xfail(reason='Need to figure out how to do select_related() on children')
@pytest.mark.usefixtures('_very_huge_tree_of_answers')
def test_descendants_query_count(api, answer, django_assert_num_queries):
    with django_assert_num_queries(100):
        api.get(f'/api/v2/homework/answers/{answer.slug}/')
