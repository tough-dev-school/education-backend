import pytest

pytestmark = [pytest.mark.django_db]


@pytest.mark.parametrize(
    ("demo_mode", "url"),
    [
        (False, "https://forma.tinkoff.ru/api/partners/v2/orders/create"),
        (True, "https://forma.tinkoff.ru/api/partners/v2/orders/create-demo"),
    ],
)
def test_create_url(tinkoff, settings, demo_mode, url):
    settings.TINKOFF_CREDIT_DEMO_MODE = demo_mode

    assert tinkoff.get_create_order_url() == url
