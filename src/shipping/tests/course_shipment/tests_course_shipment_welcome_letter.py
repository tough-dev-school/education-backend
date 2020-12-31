import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def course(course):
    course.update_from_kwargs(
        welcome_letter_template_id='tpl100500',
        gift_welcome_letter_template_id='tpl100500-gift',
    )
    course.save()

    return course


def test_the_message_is_sent_to_right_email(send_mail, shipment, user):
    shipment()()

    send_mail.assert_called_once()

    assert send_mail.call_args[1]['to'] == user.email


def test_the_message_is_sent_with_right_template_id(send_mail, shipment):
    shipment()()

    assert send_mail.call_args[1]['template_id'] == 'tpl100500'


def test_gifted_order_template_id_is_used_when_present(send_mail, shipment, gifted_order):
    shipment(order=gifted_order)()

    assert send_mail.call_args[1]['template_id'] == 'tpl100500-gift'


@pytest.mark.parametrize('empty_template_id', ['', None])
def test_the_default_template_id_used_used_with_gifted_order_but_without_gift_template_id(send_mail, shipment, gifted_order, empty_template_id):
    shipment = shipment(order=gifted_order)
    shipment.course.setattr_and_save('gift_welcome_letter_template_id', empty_template_id)

    shipment()

    assert send_mail.call_args[1]['template_id'] == 'tpl100500'


@pytest.mark.parametrize('template_id', [
    None,
    '',
])
def test_the_message_is_not_sent_when_there_is_no_template_id(send_mail, shipment, template_id):
    shipment = shipment()
    shipment.course.setattr_and_save('welcome_letter_template_id', template_id)

    send_mail.assert_not_called()


def test_antispam_is_disabled(send_mail, shipment, user):
    shipment()()

    send_mail.assert_called_once()

    assert send_mail.call_args[1]['disable_antispam'] is True
