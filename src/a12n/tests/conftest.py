import pytest


@pytest.fixture(autouse=True)
def subscribe(mocker):
    return mocker.patch('app.tasks.subscribe_to_dashamail.delay')
