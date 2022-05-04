import pytest

pytestmark = [pytest.mark.django_db]


def test_no_invitation_when_no_room_url_is_defined(shipment, invite_to_zoomus):
    shipment = shipment()

    shipment()

    invite_to_zoomus.assert_not_called()


def test_invite_to_zoomus(shipment, invite_to_zoomus, user):
    shipment = shipment()
    shipment.course.setattr_and_save('zoomus_webinar_id', '100500')

    shipment()

    invite_to_zoomus.assert_called_once_with(webinar_id='100500', user_id=user.id)
