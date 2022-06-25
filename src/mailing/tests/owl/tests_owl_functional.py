import pytest
from django.core import mail

pytestmark = [pytest.mark.django_db]


def test_sending(owl):
    owl()()

    assert len(mail.outbox) == 1


@pytest.mark.parametrize('switch', [
    lambda settings: setattr(settings, 'EMAIL_ENABLED', False),
])
def test_kill_switch(owl, switch, settings):
    switch(settings)

    owl()()

    assert len(mail.outbox) == 0


def test_attaching(owl):
    owl = owl()
    owl.attach(filename='testing_file_name_100500.txt', content=b'just testing')

    assert len(owl.msg.attachments) == 1
    assert 'testing_file_name_100500.txt' in owl.msg.attachments[0]
