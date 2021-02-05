import pytest

pytestmark = [pytest.mark.django_db]


@pytest.mark.parametrize(('demo_mode', 'url'), [
    (True, 'https://loans.tinkoff.ru/api/partners/v1/lightweight/create-demo'),
    (False, 'https://loans.tinkoff.ru/api/partners/v1/lightweight/create'),
])
def test_create_url(tinkoff, settings, demo_mode, url):
    settings.TINKOFF_CREDIT_DEMO_MODE = demo_mode

    assert tinkoff.get_create_order_url() == url
