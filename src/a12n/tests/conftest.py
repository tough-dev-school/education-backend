import pytest


@pytest.fixture(autouse=True)
def subscribe(mocker):
    return mocker.patch("app.tasks.manage_subscription_to_dashamail.delay")
