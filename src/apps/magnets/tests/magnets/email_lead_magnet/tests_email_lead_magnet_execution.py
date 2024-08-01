import pytest
from django.core import mail

from apps.mailing.models import EmailLogEntry

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def _enable_outgoing_email(settings):
    settings.EMAIL_ENABLED = True


@pytest.fixture
def user(mixer):
    return mixer.blend("users.User", email="amocrm_lead@magnet.tester")


def test_emaiL_is_sent(user, campaign):
    campaign.execute(user)

    assert len(mail.outbox) == 1


def test_email_is_sent_even_if_the_letter_was_sent_already(user, campaign):
    EmailLogEntry.objects.create(email="amocrm_lead@magnet.tester", template_id=campaign.template_id)

    campaign.execute(user)

    assert len(mail.outbox) == 1


def test_email_is_sent_to_the_right_place_with_the_right_template_id(user, campaign, send_mail):
    campaign.execute(user)

    assert send_mail.call_args[1]["to"] == "amocrm_lead@magnet.tester"
    assert send_mail.call_args[1]["template_id"] == campaign.template_id


def test_email_is_sent_with_the_right_context(user, campaign, send_mail):
    campaign.execute(user)

    ctx = send_mail.call_args[1]["ctx"]

    assert ctx["campaign_name"] == campaign.name
    assert ctx["firstname"] == user.first_name
    assert ctx["lastname"] == user.last_name
