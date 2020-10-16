import pytest
from django.core import mail

from app.mail.owl import TemplOwl

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def adjust_settings(settings):
    settings.EMAIL_ENABLED = True


@pytest.fixture
def owl():
    return TemplOwl(
        to='f@f213.in',
        template_id=100500,
    )


def test_sending(owl):
    owl.send()

    assert len(mail.outbox) == 1


@pytest.mark.parametrize('switch', [
    # lambda settings: setattr(settings, 'DISABLE_NOTIFICATIONS', True),
    lambda settings: setattr(settings, 'EMAIL_ENABLED', False),
])
def test_kill_switch(owl, switch, settings):
    switch(settings)

    owl.send()

    assert len(mail.outbox) == 0


def test_attaching(owl):
    owl.attach(filename='testing_file_name_100500.txt', content=b'just testing')

    assert len(owl.msg.attachments) == 1
    assert 'testing_file_name_100500.txt' in owl.msg.attachments[0]
