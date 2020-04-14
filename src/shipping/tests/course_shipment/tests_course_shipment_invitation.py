import pytest

pytestmark = [pytest.mark.django_db]


def test_no_invitation_when_no_room_url_is_defined(shipment, invite_to_clickmeeting, invite_to_zoomus):
    invite_to_clickmeeting.assert_not_called()
    invite_to_zoomus.assert_not_called()


def test_invite_to_clickmeeting(shipment, invite_to_clickmeeting, user):
    shipment.course.setattr_and_save('clickmeeting_room_url', 'https://room.url')

    shipment()

    invite_to_clickmeeting.assert_called_once_with(room_url='https://room.url', email=user.email)


def test_invite_to_zoomus(shipment, invite_to_zoomus, user):
    shipment.course.setattr_and_save('zoomus_webinar_id', '100500')

    shipment()

    invite_to_zoomus.assert_called_once_with(webinar_id='100500', user_id=user.id)
