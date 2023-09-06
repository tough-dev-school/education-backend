import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def api_call(mocker):
    return mocker.patch("tinkoff.dolyame.Dolyame.post", return_value={"link": "__mocked"})


def test_order_data(dolyame, order, api_call):
    dolyame.get_initial_payment_url()

    got = api_call.call_args[1]["payload"]

    assert got["order"]["id"] == order.slug
    assert got["order"]["amount"] == "100500"
    assert got["order"]["items"][0]["name"] == "Предоставление доступа к записи курса «Пентакли и Тентакли»"
    assert got["order"]["items"][0]["quantity"] == 1
    assert got["order"]["items"][0]["price"] == "100500"
    assert got["client_info"]["first_name"] == "Авраам Соломонович"
    assert "fiscalization_settings" not in got, "Should not be present in initial payment request"


def test_return_value(dolyame):
    url = dolyame.get_initial_payment_url()

    assert url == "__mocked"
