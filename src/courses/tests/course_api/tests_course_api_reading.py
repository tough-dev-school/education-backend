import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def course(mixer):
    return mixer.blend('courses.Course')


@pytest.mark.parametrize('field', [
    'name',
    'slug',
])
def test_list(api, course, field):
    got = api.get('/api/v2/courses/')['results']

    assert got[0][field] == getattr(course, field)


@pytest.mark.parametrize('field', [
    'name',
    'slug',
])
def test_retrieve(api, course, field):
    got = api.get(f'/api/v2/courses/{course.slug}/')

    assert got[field] == getattr(course, field)
