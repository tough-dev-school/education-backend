import pytest

pytestmark = [pytest.mark.django_db]


def test(anon, diploma):
    got = anon.get(f'/api/v2/diplomas/{diploma.slug}/')

    assert got['slug'] == str(diploma.slug)
    assert got['student']['uuid'] == str(diploma.study.student.uuid)
    assert got['course']['name'] == diploma.study.course.name
