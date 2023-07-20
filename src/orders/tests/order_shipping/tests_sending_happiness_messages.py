import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def _enable_happiness_messages(settings):
    settings.HAPPINESS_MESSAGES_CHAT_ID = "aaa100500"


@pytest.fixture
def tg_message(mocker):
    return mocker.patch("app.integrations.tg.send_happiness_message")


def test(tg_message, order):
    order.set_paid()

    tg_message.assert_called_once_with("💰+1500 ₽, Kamaz Otkhodov, Запись курсов катанья и мытья")


def test_no_notifications_for_already_paid_orders(tg_message, order):
    order.set_paid()
    order.set_paid()

    tg_message.assert_called_once_with("💰+1500 ₽, Kamaz Otkhodov, Запись курсов катанья и мытья")


def test_no_notifications_for_zero_prices_orders(tg_message, order):
    order.setattr_and_save("price", 0)

    order.set_paid()

    tg_message.assert_not_called()


def test_not_sending_if_disabled(settings, tg_message, order):
    settings.HAPPINESS_MESSAGES_CHAT_ID = None

    order.set_paid()

    tg_message.assert_not_called()


def test_not_sending_in_silent_mode(tg_message, order):
    order.set_paid(silent=True)

    tg_message.assert_not_called()
