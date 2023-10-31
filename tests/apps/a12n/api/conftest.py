import pytest


@pytest.fixture(autouse=True)
def subscribe(mocker):
    return mocker.patch("core.tasks.update_dashamail_subscription.delay")
