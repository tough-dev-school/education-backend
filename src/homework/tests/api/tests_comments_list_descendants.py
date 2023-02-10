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
def get_answer_comments(api, answer):
    return (
        lambda *args, **kwargs:
        api.get(f'/api/v2/homework/comments/?answer={answer.slug}', *args, **kwargs)
    )


def test_no_descendants_by_default(get_answer_comments):
    got = get_answer_comments()[0]

    assert got['descendants'] == []


def test_child_answers(get_answer_comments, another_answer):
    got = get_answer_comments()[0]

    assert len(got['descendants']) == 1


@pytest.mark.freeze_time('2022-10-09 10:30:12+12:00')  # +12 hours kamchatka timezone
@pytest.mark.usefixtures('kamchatka_timezone')
def test_child_answers_fields(get_answer_comments, answer, another_answer):
    got = get_answer_comments()[0]

    descendant = got['descendants'][0]
    assert len(descendant) == 9
    assert descendant['created'] == '2022-10-09T10:30:12+12:00'
    assert descendant['modified'] == '2022-10-09T10:30:12+12:00'
    assert descendant['slug'] == str(another_answer.slug)
    assert descendant['parent'] == str(answer.slug)
    assert descendant['question'] == str(another_answer.question.slug)
    assert descendant['author']['uuid'] == str(another_answer.author.uuid)
    assert descendant['author']['first_name'] == another_answer.author.first_name
    assert descendant['author']['last_name'] == another_answer.author.last_name
    assert 'text' in descendant
    assert 'src' in descendant
    assert 'descendants' in descendant


def test_multilevel_child_answers(get_answer_comments, another_answer, child_of_another_answer):
    got = get_answer_comments()[0]

    assert got['descendants'][0]['slug'] == str(another_answer.slug)
    assert got['descendants'][0]['descendants'][0]['slug'] == str(child_of_another_answer.slug)
    assert got['descendants'][0]['descendants'][0]['descendants'] == []


@pytest.mark.usefixtures('child_of_another_answer')
def test_only_immediate_siblings_are_included(get_answer_comments):
    got = get_answer_comments()[0]

    assert len(got['descendants']) == 1


@pytest.mark.usefixtures('another_answer', 'child_of_another_answer')
def test_reasonable_nplusone_queries_for_answers_with_descendants(get_answer_comments, django_assert_num_queries):
    with django_assert_num_queries(10):
        get_answer_comments()[0]
