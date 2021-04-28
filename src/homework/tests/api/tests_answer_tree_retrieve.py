import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures('purchase'),
]


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
    another_answer.parent = answer
    another_answer.save()

    got = api.get(f'/api/v2/homework/answers/{answer.slug}/')

    assert got['descendants'][0]['slug'] == str(another_answer.slug)
    assert got['descendants'][0]['author']['first_name'] == api.user.first_name
    assert got['descendants'][0]['author']['last_name'] == api.user.last_name


def test_multilevel_child_answers(api, answer, another_answer, child_of_another_answer):
    another_answer.parent = answer
    another_answer.save()

    got = api.get(f'/api/v2/homework/answers/{answer.slug}/')

    assert got['descendants'][0]['slug'] == str(another_answer.slug)
    assert got['descendants'][0]['descendants'][0]['slug'] == str(child_of_another_answer.slug)
    assert got['descendants'][0]['descendants'][0]['descendants'] == []


@pytest.mark.usefixtures('child_of_another_answer')
def test_only_immediate_siblings_are_included(api, answer, another_answer):
    another_answer.parent = answer
    another_answer.save()

    got = api.get(f'/api/v2/homework/answers/{answer.slug}/')

    assert len(got['descendants']) == 1


@pytest.mark.xfail(reason='WIP')
@pytest.mark.usefixtures('_very_huge_tree_of_answers')
def test_descendants_query_count(api, answer, django_assert_num_queries):
    with django_assert_num_queries(100):
        api.get(f'/api/v2/homework/answers/{answer.slug}/')
