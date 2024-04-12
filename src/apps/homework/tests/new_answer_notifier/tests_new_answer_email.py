import pytest

pytestmark = [pytest.mark.django_db]


def test(notifier, answer, another_answer, send_mail, mocker):
    answer.update(parent=another_answer)

    notifier(answer)()

    send_mail.assert_called_once_with(
        to=another_answer.author.email,
        disable_antispam=True,
        template_id="new-answer-notification",
        ctx=mocker.ANY,
    )
