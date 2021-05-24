import pytest


@pytest.fixture
def send_mail(mocker):
    return mocker.patch('app.tasks.send_mail.delay')
