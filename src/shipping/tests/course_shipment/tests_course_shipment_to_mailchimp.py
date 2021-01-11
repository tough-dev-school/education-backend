import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def subscribe_to_mailchimp(mocker):
    return mocker.patch('app.tasks.subscribe_to_mailchimp.delay')


def test(shipment, user, subscribe_to_mailchimp):
    shipment = shipment()
    shipment.course.setattr_and_save('mailchimp_list_id', '100500')

    shipment()

    subscribe_to_mailchimp.assert_called_once_with(
        list_id='100500',
        user_id=user.id,
        tags=['sewing'],
    )


def test_not_called_if_there_is_no_contact_list_id(shipment, user, subscribe_to_mailchimp):
    shipment()()

    subscribe_to_mailchimp.assert_not_called()
