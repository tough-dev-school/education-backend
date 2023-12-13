import pytest
from apps.dashamail.directcrm import events


pytestmark = [pytest.mark.django_db]


def test_order_created(order):
    event = events.OrderCreated(order)

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


def test_order_paid(order):
    event = events.OrderPaid(order)

    assert event.to_json() == {
        "customer": {
            "email": "big@guy.com",
        },
        "order": {
            "orderId": order.slug,
            "status": "finished",
            "totalPrice": "100500,65",
            "lines": [{
                "price": "100500,65",
                "productId": "aa-5-full",
                "quantity": 1,
            }],
        },

    }
