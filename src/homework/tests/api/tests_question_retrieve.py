import pytest

pytestmark = [pytest.mark.django_db]


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
