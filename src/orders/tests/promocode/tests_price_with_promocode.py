import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures('promocode'),
]


@pytest.mark.parametrize('code', [
    'TESTCODE',
    'testcode',
])
def test(api, course, code):
    got = api.get(f'/api/v2/courses/{course.slug}/promocode/?promocode={code}')

    assert got['price'] == 90450
    assert got['formatted_price'] == '90 450'


@pytest.mark.parametrize('code', [
    'EV1L',
    '',
])
def test_bad_promocode(api, course, code):
    got = api.get(f'/api/v2/courses/{course.slug}/promocode/?promocode={code}')

    assert got['price'] == 100500


def test_incompatible_promocode(api, course, another_course, promocode):
    promocode.courses.add(course)

    got = api.get(f'/api/v2/courses/{another_course.slug}/promocode/?promocode=TESTCODE')

    assert got['price'] == 100500


def test_compatible_promocode(api, course, promocode):
    promocode.courses.add(course)

    got = api.get(f'/api/v2/courses/{course.slug}/promocode/?promocode=TESTCODE')

    assert got['price'] == 90450


def test_wihtout_promocode(api, course):
    api.get(
        f'/api/v2/courses/{course.slug}/promocode/', expected_status_code=400,
    )
