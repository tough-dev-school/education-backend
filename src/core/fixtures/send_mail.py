import pytest


@pytest.fixture
def send_mail(mocker):
    return mocker.patch("apps.mailing.tasks.send_mail.delay")
