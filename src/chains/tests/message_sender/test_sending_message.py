import contextlib
import httpx
import pytest

from chains.models import Progress

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def send_message(message_sender, message, study):
    return message_sender(message, study)


def test_message_is_sent(send_message, message, study, owl):
    send_message()

    owl.assert_called_once_with(
        ctx={
            'firstname': study.student.first_name,
            'lastname': study.student.last_name,
        },
        disable_antispam=False,
        template_id=message.template_id,
        to=study.student.email,
        subject='',
    )


def test_message_is_sent_only_once(send_message, message, study, owl):
    send_message()
    send_message()

    owl.assert_called_once()


def test_message_is_not_sent_when_progress_record_exists(send_message, message, study, owl):
    Progress.objects.create(message=message, study=study)

    send_message()

    owl.assert_not_called()


def test_progress_is_saved(send_message, message, study):
    send_message()

    assert Progress.objects.filter(message=message, study=study).exists()


def test_progress_is_not_saved_when_message_is_not_sent(send_message, message, study, owl):
    owl.side_effect = httpx.ConnectTimeout('test error')

    with contextlib.suppress(httpx.ConnectTimeout):
        send_message()

    assert not Progress.objects.filter(message=message, study=study).exists()
