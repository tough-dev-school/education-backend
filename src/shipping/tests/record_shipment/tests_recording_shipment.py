import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def send_mail(mocker):
    return mocker.patch('app.tasks.send_mail.delay')


def test_the_message_is_sent_to_email(send_mail, shipment, user):
    shipment()

    send_mail.assert_called_once()
    assert send_mail.call_args[1]['to'] == user.email


def test_antispam_is_disabled(send_mail, shipment, user):
    shipment()

    send_mail.assert_called_once()

    assert send_mail.call_args[1]['disable_antispam'] is True
