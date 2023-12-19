import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def confirmed_order(order):
    order.set_paid()

    return order


def test_respose(anon, order):
    response = anon.get(f"/api/v2/orders/{order.slug}/confirm/", as_response=True)

    assert response.status_code == 302
    assert response["location"] == "https://well.done"


def test_response_on_already_confirmed_order(anon, confirmed_order):
    response = anon.get(f"/api/v2/orders/{confirmed_order.slug}/confirm/", as_response=True)

    assert response.status_code == 302
    assert response["location"] == "https://well.done"


def test_unconfirmed_order_ships(anon, order, ship):
    anon.get(f"/api/v2/orders/{order.slug}/confirm/", expected_status_code=302)

    order.refresh_from_db()
    ship.assert_called_once_with(order=order, to=order.user)
    assert order.paid is not None


def test_order_is_shipped_only_one_time(anon, order, ship):
    for _ in range(3):
        anon.get(f"/api/v2/orders/{order.slug}/confirm/", expected_status_code=302)

    ship.assert_called_once_with(order=order, to=order.user)


def test_404_for_non_zero_priced_orders(anon, order, ship):
    order.update(price=100500)

    anon.get(f"/api/v2/orders/{order.slug}/confirm/", expected_status_code=404)

    ship.assert_not_called()
