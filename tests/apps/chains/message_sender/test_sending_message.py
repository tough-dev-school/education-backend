import pytest

from anymail.exceptions import AnymailRecipientsRefused

from apps.chains.models import Progress

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def send_message(message_sender, message, study):
    return message_sender(message, study)


def test_message_is_sent(send_message, message, study, owl):
    send_message()

    owl.assert_called_once_with(
        ctx={
            "firstname": study.student.first_name,
            "lastname": study.student.last_name,
        },
        disable_antispam=False,
        template_id=message.template_id,
        to=study.student.email,
        subject="",
    )


def test_message_is_sent_only_once(send_message, message, study, owl):
    send_message()
    send_message()

    owl.assert_called_once()


@pytest.mark.parametrize("success", [True, False])
def test_message_is_not_sent_when_progress_record_exists(send_message, message, study, owl, success):
    Progress.objects.create(message=message, study=study, success=success)

    send_message()

    owl.assert_not_called()


def test_progress_is_saved(send_message, message, study):
    send_message()

    assert Progress.objects.filter(message=message, study=study, success=True).exists()


@pytest.mark.xfail(strict=True, reason="Seems there is no way of testing link_error in the eager mode")
@pytest.mark.parametrize(
    "exc",
    [
        AnymailRecipientsRefused,
    ],
)
def test_progress_status_is_saved_when_message_is_not_sent(send_message, message, study, owl, exc):
    owl.side_effect = exc("Test Error")

    send_message()

    assert Progress.objects.filter(message=message, study=study, success=False).exists()
