import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def course(mixer):
    return mixer.blend('courses.Course', price='500', old_price='500.95')


def test_list(api, course):
    got = api.get('/api/v2/courses/')['results']

    assert got[0]['price'] == '500'
    assert got[0]['old_price'] == '500,95'


def test_retrieve(api, course):
    got = api.get(f'/api/v2/courses/{course.slug}/')

    assert got['price'] == '500'
    assert got['old_price'] == '500,95'
