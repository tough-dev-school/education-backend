import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def _enable_happiness_messages(settings):
    settings.SEND_HAPPINESS_MESSAGES = True


@pytest.fixture
def tg_message(mocker):
    return mocker.patch('app.integrations.tg.send_happiness_message')


def test(tg_message, order):
    order.set_paid()

    tg_message.assert_called_once_with('💰+1500 ₽, Kamaz Otkhodov, Запись курсов катанья и мытья')


def test_gift(tg_message, order, another_user):
    order.setattr_and_save('giver', another_user)
    order.set_paid()

    tg_message.assert_called_once_with('💰+1500 ₽, Kamaz Otkhodov, Запись курсов катанья и мытья (подарок)')


def test_not_sending_if_disabled(settings, tg_message, order):
    settings.SEND_HAPPINESS_MESSAGES = False

    order.set_paid()

    tg_message.assert_not_called()


def test_not_sending_in_silent_mode(settings, tg_message, order):
    order.set_paid(silent=True)

    tg_message.assert_not_called()
