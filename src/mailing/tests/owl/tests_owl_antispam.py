import pytest
from django.core import mail
from functools import partial

from app.models import EmailLogEntry
from mailing.owl import Owl
from mailing.tasks import send_mail

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def _enable_email(settings):
    settings.EMAIL_ENABLED = True


@pytest.fixture
def owl():
    return partial(
        Owl,
        to='f@f213.in',
        template_id=100500,
    )


def email_log_entry_exists(**kwargs) -> bool:
    return EmailLogEntry.objects.filter(**kwargs).exists()


def test_log_entry_is_created(owl):
    owl()()

    assert email_log_entry_exists(email='f@f213.in', template_id=100500) is True


def test_when_log_entry_already_exists_all_is_ok(owl):
    EmailLogEntry.objects.create(email='f@f213.in', template_id=100500)

    owl(disable_antispam=True)()


@pytest.mark.parametrize(('disable_antispam', 'should_email_be_sent'), [
    (False, False),
    (True, True),
])
def test_mail_is_not_sent_when_log_entry_already_exists(owl, disable_antispam, should_email_be_sent):
    EmailLogEntry.objects.create(email='f@f213.in', template_id=100500)

    owl(disable_antispam=disable_antispam)()

    assert (len(mail.outbox) == 1) is should_email_be_sent


@pytest.mark.parametrize(('disable_antispam', 'should_email_be_sent'), [
    (False, False),
    (True, True),
])
def test_antispam_arg_is_passed_via_task(disable_antispam, should_email_be_sent):
    EmailLogEntry.objects.create(email='f@f213.in', template_id=100500)

    send_mail.delay(to='f@f213.in', template_id=100500, disable_antispam=disable_antispam)

    assert (len(mail.outbox) == 1) is should_email_be_sent
