import pytest

pytestmark = [pytest.mark.django_db]


def test_template_context(shipment):
    ctx = shipment.get_template_context()

    assert ctx['name'] == 'Кройка и шитьё'
    assert ctx['name_genitive'] == 'Кройки и шитья'
