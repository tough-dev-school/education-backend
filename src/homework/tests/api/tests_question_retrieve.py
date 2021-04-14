import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures('purchase'),
]


def test_ok(api, question, course):
    got = api.get(f'/api/v2/homework/questions/{question.slug}/')

    assert got['slug'] == str(question.slug)
    assert got['name'] == question.name
    assert got['course']['slug'] == str(course.slug)
    assert got['course']['name'] == course.name
    assert got['course']['full_name'] == course.full_name


def test_markdown(api, question):
    question.setattr_and_save('text', '*should be rendered*')

    got = api.get(f'/api/v2/homework/questions/{question.slug}/')

    assert '<em>should be rendered' in got['text']


def test_401_for_not_purchased_users(api, question, purchase):
    purchase.setattr_and_save('paid', None)

    api.get(f'/api/v2/homework/questions/{question.slug}/', expected_status_code=403)


def test_no_anon(anon, question):
    anon.get(f'/api/v2/homework/questions/{question.slug}/', expected_status_code=401)
