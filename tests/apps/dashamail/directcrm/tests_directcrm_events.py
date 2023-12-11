import pytest
from apps.dashamail.directcrm.events import OrderCreated


pytestmark = [pytest.mark.django_db]


def test(order):
    event = OrderCreated(order)

    assert event.to_json() == {
        "customer": {
            "email": "big@guy.com",
        },
        "order": {
            "orderId": order.slug,
            "status": "created",
            "totalPrice": "100500,65",
            "lines": [{
                "price": "100500,65",
                "productId": "aa-5-full",
                "quantity": 1,
            }],
        },

    }
