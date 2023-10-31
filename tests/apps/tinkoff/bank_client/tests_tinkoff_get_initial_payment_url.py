import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def req(mocker):
    return mocker.patch(
        "apps.tinkoff.bank.TinkoffBank.call",
        return_value={
            "PaymentURL": "https://mocked.in.fixture/",
        },
    )


def test_ok_initial_payment_url(tinkoff):
    tinkoff.m.post("https://securepay.tinkoff.ru/v2/Init/").respond(
        json={
            "Success": True,
            "PaymentURL": "https://pay.ment/url",
        },
    )

    assert tinkoff.get_initial_payment_url() == "https://pay.ment/url"


def test_initial_payment_url_payload(tinkoff, req, settings):
    assert tinkoff.get_initial_payment_url() == "https://mocked.in.fixture/"

    payload = req.call_args[1]["payload"]

    assert payload["OrderId"] == tinkoff.order.slug
    assert payload["CustomerKey"] == tinkoff.order.user.id

    assert "https://" in payload["SuccessURL"]
    assert "https://" in payload["FailURL"]

    assert "Receipt" in payload
    assert "NotificationURL" in payload


def test_notification_url(tinkoff):
    assert tinkoff.get_notification_url() == "https://tst.hst/api/v2/banking/tinkoff-notifications/"
