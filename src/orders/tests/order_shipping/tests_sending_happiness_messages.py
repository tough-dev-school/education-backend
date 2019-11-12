import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def enable_happiness_messages(settings):
    settings.SEND_HAPPINESS_MESSAGES = True


@pytest.fixture
def tg_message(mocker):
    return mocker.patch('app.tg.send_happiness_message')


def test(tg_message, order):
    order.set_paid()

    tg_message.assert_called_once_with('💰+1500 ₽, Kamaz Otkhodov, Запись курсов катанья и мытья')


def test_not_sending_if_disabled(settings, tg_message, order):
    settings.SEND_HAPPINESS_MESSAGES = False

    order.set_paid()

    tg_message.assert_not_called()
