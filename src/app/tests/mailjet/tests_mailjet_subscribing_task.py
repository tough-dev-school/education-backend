import pytest
from django.core.exceptions import ImproperlyConfigured

from app.tasks import subscribe_to_mailjet

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def subscribe(mocker):
    return mocker.patch('app.mailjet.AppMailjet.subscribe')


def test(subscribe, user):
    subscribe_to_mailjet(user.id, 100500)

    subscribe.assert_called_once_with(user, 100500)


@pytest.mark.xfail(raises=ImproperlyConfigured)
@pytest.mark.parametrize('setting', [
    'MAILJET_API_KEY',
    'MAILJET_SECRET_KEY',
])
def test_subscription_is_disabled_if_any_single_setting_is_disabled(user, setting, settings):
    setattr(settings, setting, '')

    subscribe_to_mailjet(user.id, 100500)
