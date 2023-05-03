import pytest


@pytest.fixture
def send_mail(mocker):
    return mocker.patch("mailing.tasks.send_mail.delay")
