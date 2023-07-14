import pytest


@pytest.fixture(autouse=True)
def subscribe(mocker):
    return mocker.patch("app.tasks.update_dashamail_subscription.delay")
