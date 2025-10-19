from decimal import Decimal

import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def send_message(mocker):
    return mocker.patch("apps.b2b.services.deal_completer.send_telegram_message.delay")


@pytest.fixture(autouse=True)
def _set_happiness_chat_id(settings):
    settings.HAPPINESS_MESSAGES_CHAT_ID = 100500


def test_no_message_sent_if_no_chat_id_defined(settings, send_message, completer, deal):
    settings.HAPPINESS_MESSAGES_CHAT_ID = None

    completer(deal=deal)()

    send_message.assert_not_called()


def test_no_message_if_shipped_without_payment(send_message, completer, deal):
    completer(deal=deal, ship_only=True)()

    send_message.assert_not_called()


def test_message_is_sent(send_message, completer, deal):
    completer(deal=deal)()

    assert send_message.call_count == 1
    assert send_message.call_args[1]["chat_id"] == 100500


def test_message_text(send_message, completer, deal):
    deal.price = Decimal(200500)
    deal.customer.name = "Росатом"
    deal.course.product_name = "Противопожарная безопасность"

    completer(deal=deal)()

    assert str(deal.author) in send_message.call_args[1]["text"]
    assert "200\xa0500 ₽" in send_message.call_args[1]["text"]
    assert "Росатом" in send_message.call_args[1]["text"]
    assert "безопасность" in send_message.call_args[1]["text"]


@pytest.mark.usefixtures("usd")
def test_currency(send_message, completer, deal):
    deal.update(price=Decimal(100), currency="usd")

    completer(deal=deal)()

    assert "100 $" in send_message.call_args[1]["text"]
