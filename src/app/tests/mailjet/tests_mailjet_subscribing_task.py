import pytest

from app.tasks import subscribe_to_mailjet

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def subscribe(mocker):
    return mocker.patch('app.mailjet.AppMailjet.subscribe')


def test(subscribe, user):
    subscribe_to_mailjet.delay(user.id)

    subscribe.assert_called_once_with(user)
