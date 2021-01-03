import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def bundle(mixer):
    return mixer.blend('products.Bundle', slug='pinetree-tickets', name='Флаг и билет на ёлку', price='500', old_price='500.95')


def test_list(api, bundle):
    got = api.get('/api/v2/bundles/')['results']

    assert got[0]['price'] == '500'
    assert got[0]['old_price'] == '500,95'
    assert got[0]['formatted_price'] == '5̶0̶0̶,̶9̶5̶ 500 ₽'


def test_retrieve(api, bundle):
    got = api.get(f'/api/v2/bundles/{bundle.slug}/')

    assert got['price'] == '500'
    assert got['old_price'] == '500,95'
    assert got['formatted_price'] == '5̶0̶0̶,̶9̶5̶ 500 ₽'
