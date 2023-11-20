import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def course(course):
    return course.update(welcome_letter_template_id="tpl100500")


def test_the_message_is_sent_to_right_email(send_mail, shipment, user):
    shipment()()

    send_mail.assert_called_once()

    assert send_mail.call_args[1]["to"] == user.email


def test_the_message_is_sent_with_right_template_id(send_mail, shipment):
    shipment()()

    assert send_mail.call_args[1]["template_id"] == "tpl100500"


@pytest.mark.parametrize(
    "template_id",
    [
        None,
        "",
    ],
)
def test_the_message_is_not_sent_when_there_is_no_template_id(send_mail, shipment, template_id):
    shipment = shipment()
    shipment.course.update(welcome_letter_template_id=template_id)

    send_mail.assert_not_called()


def test_antispam_is_disabled(send_mail, shipment, user):
    shipment()()

    send_mail.assert_called_once()

    assert send_mail.call_args[1]["disable_antispam"] is True
