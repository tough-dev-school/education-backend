import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def record(mixer):
    return mixer.blend('courses.Record', price='500', old_price='500.95')


def test_list(api, record):
    got = api.get('/api/v2/records/')['results']

    assert got[0]['price'] == '500'
    assert got[0]['old_price'] == '500,95'


def test_retrieve(api, record):
    got = api.get(f'/api/v2/records/{record.slug}/')

    assert got['price'] == '500'
    assert got['old_price'] == '500,95'
