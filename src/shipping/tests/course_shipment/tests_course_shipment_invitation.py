import pytest

pytestmark = [pytest.mark.django_db]


def test(shipment, invite, user):
    shipment()

    invite.assert_called_once_with(room_url='https://room.url', email=user.email)


def test_no_invitation_when_no_room_url_is_defined(shipment, invite):
    shipment.course.setattr_and_save('room_url', None)

    invite.assert_not_called()
