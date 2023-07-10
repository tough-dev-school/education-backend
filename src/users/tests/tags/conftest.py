import pytest


@pytest.fixture
def user(user):
    user.tags = []
    user.save()
    return user


@pytest.fixture(autouse=True)
def _mock_subscribe_to_dashamail(mocker):
    mocker.patch("app.integrations.dashamail.helpers.subscribe_user_to_dashamail")
