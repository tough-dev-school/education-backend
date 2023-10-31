import pytest


@pytest.fixture(autouse=True)
def _mock_subscription_updater(mocker):  # global mock for Dashamail
    mocker.patch("core.integrations.dashamail.subscription_updater.SubscriptionUpdater.__call__")
