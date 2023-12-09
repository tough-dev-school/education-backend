import pytest
from apps.dashamail.directcrm.events import OrderCreated


pytestmark = [pytest.mark.django_db]


@pytest.fixture
def order(factory, course):
    return factory.order(item=course, is_paid=False, price='100500.65')


def test(order):
    event = OrderCreated(order)

    assert event.to_json() == {
        "orderId": order.slug,
        "status": "created",
        "totalPrice": "100500.65",
        "lines": [{
            "price": "100500.65",
            "productId": "aa-5-full",
            "quantity": 1,
        }],

    }
