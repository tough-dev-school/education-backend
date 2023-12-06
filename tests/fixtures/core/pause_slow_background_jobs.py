import pytest


@pytest.fixture(autouse=True)
def _mock_subscription_updater(mocker):  # global mock for Dashamail
    mocker.patch("apps.dashamail.lists.client.DashamailListsClient.subscribe_or_update")
