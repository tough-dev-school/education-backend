import pytest

from core import tasks

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def subscription_updater(mocker):
    mocker.patch("core.integrations.dashamail.subscription_updater.SubscriptionUpdater.__call__")
    return mocker.patch("core.integrations.dashamail.subscription_updater.SubscriptionUpdater.__init__", return_value=None)


def test_task(user, subscription_updater):
    tasks.update_dashamail_subscription.delay(user.pk)

    subscription_updater.assert_called_once_with(user)
