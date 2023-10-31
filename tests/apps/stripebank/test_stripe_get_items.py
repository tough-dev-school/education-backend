import pytest

pytestmark = [pytest.mark.django_db]


def test_item(stripe):
    result = stripe.get_items()

    assert result == [
        {
            "price_data": {
                "currency": "eur",
                "product_data": {
                    "name": "Cutting and Sewing",
                },
                "unit_amount": 143600,
            },
            "quantity": 1,
        },
    ]


@pytest.mark.parametrize(
    ("price", "expected"),
    [
        (70, 100),
        (140, 200),
        (95, 100),
        (105, 200),
    ],
)
def test_price(stripe, price, expected):
    stripe.order.update(price=price)

    result = stripe.get_items()

    assert result[0]["price_data"]["unit_amount"] == expected
