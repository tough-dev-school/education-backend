import pytest

from tinkoff.bank import TinkoffBank

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def paid_tinkoff_order(order, mixer):
    order.setattr_and_save("bank_id", "tinkoff_bank")
    order.set_paid()

    mixer.blend("tinkoff.PaymentNotification", order=order, payment_id=9001)
    return order


@pytest.fixture
def refund_success_response():
    return {
        "Success": True,
        "ErrorCode": "0",
        "TerminalKey": "k3y",
        "Status": "REFUNDED",
        "PaymentId": "9001",
        "OrderId": "8P4GtFYc3fuaoVTTMa9EZt",
        "OriginalAmount": 10050000,
        "NewAmount": 0,
    }


@pytest.fixture(autouse=True)
def add_tinkoff_refund_response(respx_mock, refund_success_response):
    return respx_mock.post("https://securepay.tinkoff.ru/v2/Cancel/").respond(json=refund_success_response)


@pytest.fixture
def tinkoff(paid_tinkoff_order):
    return TinkoffBank(order=paid_tinkoff_order)


def test_send_correct_refund_request(tinkoff, retrieve_request_json):
    tinkoff.refund()

    refund_request = retrieve_request_json()
    assert refund_request["PaymentId"] == 9001
    assert "Receipt" in refund_request
    assert "TerminalKey" in refund_request
    assert "Token" in refund_request
