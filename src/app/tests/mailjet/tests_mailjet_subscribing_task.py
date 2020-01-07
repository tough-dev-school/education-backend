import pytest

from app.tasks import subscribe_to_mailjet

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def subscribe(mocker):
    return mocker.patch('app.mailjet.AppMailjet.subscribe')


def test(subscribe, user, subscribe_list):
    subscribe_to_mailjet(user.id, subscribe_list)

    subscribe.assert_called_once_with(user, subscribe_list)


@pytest.mark.parametrize('setting', [
    'MAILJET_API_KEY',
    'MAILJET_SECRET_KEY',
])
def test_subscription_is_disabled_if_any_single_setting_is_disabled(subscribe, user, setting, settings, subscribe_list):
    setattr(settings, setting, '')

    subscribe_to_mailjet(user.id, subscribe_list)

    subscribe.assert_not_called()
