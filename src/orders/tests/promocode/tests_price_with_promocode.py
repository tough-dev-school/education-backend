import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def course(mixer):
    return mixer.blend('courses.Course', price=100500)


@pytest.fixture(autouse=True)
def testcode(mixer):
    return mixer.blend('orders.PromoCode', discount_percent=10, name='TESTCODE')


@pytest.mark.parametrize('promocode', [
    'TESTCODE',
    'testcode',
])
def test(api, course, promocode):
    got = api.get(f'/api/v2/courses/{course.slug}/promocode/?promocode={promocode}')

    assert got['price'] == 90450
    assert got['formatted_price'] == '90 450'


@pytest.mark.parametrize('promocode', [
    'EV1L',
    '',
])
def test_bad_promocode(api, course, promocode):
    got = api.get(f'/api/v2/courses/{course.slug}/promocode/?promocode={promocode}')

    assert got['price'] == 100500


def test_wihtout_promocode(api, course):
    api.get(
        f'/api/v2/courses/{course.slug}/promocode/', expected_status_code=400,
    )
