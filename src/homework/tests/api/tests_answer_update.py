import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures('purchase'),
]


@pytest.fixture
def answer_of_another_author(mixer, question, another_user):
    return mixer.blend('homework.Answer', question=question, author=another_user)


def test_changing_text(api, answer):
    api.patch(f'/api/v2/homework/answers/{answer.slug}/', {'text': '*patched*'})

    answer.refresh_from_db()

    assert answer.text == '*patched*'


@pytest.mark.xfail(reason='WIP: will add per-course permissions later')
@pytest.mark.usefixtures('_no_purchase')
def test_403_without_a_purchase(api, answer):
    api.patch(f'/api/v2/homework/answers/{answer.slug}/', {'text': '*patched*'}, expected_status_code=403)


def test_404_for_answer_of_another_author(api, answer_of_another_author):
    api.patch(f'/api/v2/homework/answers/{answer_of_another_author.slug}/', {'text': '*patched*'}, expected_status_code=404)


def test_changing_text_response(api, answer):
    got = api.patch(f'/api/v2/homework/answers/{answer.slug}/', {'text': '*patched*'})

    assert got['src'] == '*patched*'
    assert '<em>patched</em>' in got['text']
