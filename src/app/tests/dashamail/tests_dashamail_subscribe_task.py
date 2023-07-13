import pytest

from app import tasks

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def subscription_updater(mocker):
    return mocker.patch("app.integrations.dashamail.subscription_updater.SubscriptionUpdater.__init__", return_value=None)


def test_task_when_user_exist_and_inactive(user, subscription_updater):
    tasks.update_dashamail_subscription.delay(user.pk, "123")

    subscription_updater.assert_called_once_with(user, "123")
