import pytest

pytestmark = [pytest.mark.django_db]


def test_template_context(shipment):
    ctx = shipment().get_template_context()

    assert ctx["name"] == "Кройка и шитьё"
    assert ctx["name_genitive"] == "Кройки и шитья"

    assert "giver_name" not in ctx
    assert "gift_message" not in ctx


def test_gift_template_context(shipment, gifted_order):
    shipment = shipment(order=gifted_order)

    ctx = shipment.get_template_context()

    assert ctx["giver_name"] == "Робин Бетмен"
    assert ctx["gift_message"] == "Гори в аду!"
