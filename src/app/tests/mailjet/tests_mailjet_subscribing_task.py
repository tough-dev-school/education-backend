import pytest

from app.tasks import subscribe_to_mailjet

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def subscribe(mocker):
    return mocker.patch('app.integrations.mailjet.AppMailjet.subscribe')


def test(subscribe, user):
    subscribe_to_mailjet(user.id)

    subscribe.assert_called_once_with(user)


@pytest.mark.parametrize('setting', [
    'MAILJET_API_KEY',
    'MAILJET_SECRET_KEY',
    'MAILJET_CONTACT_LIST_ID',
])
def test_subscription_is_disabled_if_any_single_setting_is_disabled(subscribe, user, setting, settings):
    setattr(settings, setting, '')

    subscribe_to_mailjet(user.id)

    subscribe.assert_not_called()
