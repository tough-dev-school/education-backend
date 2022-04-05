import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def subscribe_to_dashamail(mocker):
    return mocker.patch('app.tasks.subscribe_to_dashamail.delay')


@pytest.fixture
def unsubscribe_from_dashamail(mocker):
    return mocker.patch('app.tasks.unsubscribe_from_dashamail.delay')


def test_ship(shipment, user, subscribe_to_dashamail):
    shipment = shipment()
    shipment.course.setattr_and_save('dashamail_list_id', '100500')

    shipment()

    subscribe_to_dashamail.assert_called_once_with(
        list_id='100500',
        user_id=user.id,
        tags=['sewing', 'sewing-purchased'],
    )


def test_unship(shipment, user, unsubscribe_from_dashamail):
    shipment = shipment()
    shipment.course.setattr_and_save('dashamail_list_id', '100500')

    shipment()
    shipment.unship()

    unsubscribe_from_dashamail.assert_called_once_with(
        list_id='100500',
        user_id=user.id,
    )


def test_not_called_if_there_is_no_contact_list_id(shipment, subscribe_to_dashamail):
    shipment()()

    subscribe_to_dashamail.assert_not_called()
