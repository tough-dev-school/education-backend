import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def giver(mixer):
    return mixer.blend('users.User')


@pytest.fixture
def order(order, giver):
    order.setattr_and_save('giver', giver)
    order.setattr_and_save('desired_shipment_date', '2021-01-01 15:30')

    order.refresh_from_db()

    return order


def test_mail_is_sent(order, send_mail):
    order.set_paid()

    send_mail.assert_called_once()


def test_mail_is_not_sent_when_order_has_no_giver(order, send_mail, giver):
    order.setattr_and_save('giver', None)
    order.set_paid()

    send_mail.assert_not_called()


def test_email_is_sent_the_right_way(order, send_mail, giver):
    order.set_paid()

    assert send_mail.call_args[1]['to'] == giver.email


def test_order_is_marked_as_order_with_notification_sent_to_gver(order, giver):
    assert order.notification_to_giver_is_sent is False
    order.set_paid()

    order.refresh_from_db()

    assert order.notification_to_giver_is_sent is True


def test_email_is_not_sent_when_it_is_already_sent(order, send_mail, giver):
    order.setattr_and_save('notification_to_giver_is_sent', True)

    order.set_paid()

    send_mail.assert_not_called()


def test_email_context(order, send_mail):
    order.set_paid()

    ctx = send_mail.call_args[1]['ctx']

    assert ctx['item_name'] == 'Полная запись курса катанья и мытья'
    assert ctx['receiver_name'] == 'Kamaz Otkhodov'
    assert ctx['receiver_email'] == 'kamaz@gmail.com'
    assert ctx['desired_shipment_date'] == '01.01.2021'
