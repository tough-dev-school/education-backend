import pytest

from apps.banking.selector import BANK_KEYS
from apps.banking.selector import BANKS
from apps.orders.services import OrderShipper

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def _adjust_settings(settings):
    settings.HAPPINESS_MESSAGES_CHAT_ID = "aaa100500"
    settings.LANGUAGE_CODE = "en"


@pytest.fixture(autouse=True)
def tg_message(mocker):
    return mocker.patch("core.integrations.tg.send_message")


@pytest.fixture
def mock_get_happiness_message(mocker):
    return mocker.patch("apps.orders.services.order_shipper.OrderShipper.get_order_happiness_message", return_value="happiness_message")


def test(tg_message, order, mock_get_happiness_message):
    order.set_paid()

    mock_get_happiness_message.assert_called_once_with(order)
    tg_message.assert_called_once_with(
        chat_id="aaa100500",
        text="happiness_message",
    )


def test_no_notifications_for_already_paid_orders(tg_message, order, mock_get_happiness_message):
    order.set_paid()
    order.set_paid()

    tg_message.assert_called_once_with(
        chat_id="aaa100500",
        text="happiness_message",
    )


def test_no_notifications_for_zero_prices_orders(tg_message, order):
    order.update(price=0)

    order.set_paid()

    tg_message.assert_not_called()


def test_not_sending_if_disabled(settings, tg_message, order):
    settings.HAPPINESS_MESSAGES_CHAT_ID = None

    order.set_paid()

    tg_message.assert_not_called()


def test_not_sending_in_silent_mode(tg_message, order):
    order.set_paid(silent=True)

    tg_message.assert_not_called()


@pytest.mark.parametrize("bank_id", BANK_KEYS)
def test_notification_message_include_payment_method(order, bank_id):
    order.update(bank_id=bank_id)
    order.set_paid()

    message = OrderShipper.get_order_happiness_message(order)

    assert message == f"💰+1500 ₽, {BANKS[bank_id].name}\nЗапись курсов катанья и мытья\nKamaz Otkhodov"


def test_include_promocode_if_set(order, mixer):
    order.update(promocode=mixer.blend("orders.PromoCode", name="YARR!", discount_percent=1))
    order.set_paid()

    message = OrderShipper.get_order_happiness_message(order)

    assert message == "💰+1500 ₽, Tinkoff, промокод YARR!\nЗапись курсов катанья и мытья\nKamaz Otkhodov"


def test_include_group_if_set(order, factory):
    order.item.update(group=factory.group(name="Эффективная прокрастинация поток 2"))
    order.set_paid()

    message = OrderShipper.get_order_happiness_message(order)

    assert message == "💰+1500 ₽, Tinkoff\nЗапись курсов катанья и мытья - Эффективная прокрастинация поток 2\nKamaz Otkhodov"
