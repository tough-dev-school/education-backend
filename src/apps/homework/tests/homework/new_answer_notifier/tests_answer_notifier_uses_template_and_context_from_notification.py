import pytest

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def _notification(mocker):
    mocker.patch(
        "apps.homework.services.new_answer_notifier.CrossCheckedAnswerNotification.get_context",
        return_value={"__mocked": True},
    )
    mocker.patch(
        "apps.homework.services.new_answer_notifier.CrossCheckedAnswerNotification.get_template_id",
        return_value="n0t1f1cat10n",
    )
    mocker.patch(
        "apps.homework.services.new_answer_notifier.CrossCheckedAnswerNotification.should_send",
        return_value=True,
    )


def test_sends_notification(notifier, answer, another_answer, send_mail):
    answer.update(parent=another_answer)

    notifier(answer)()

    send_mail.assert_called_once_with(
        to=another_answer.author.email,
        template_id="n0t1f1cat10n",
        ctx={"__mocked": True},
        disable_antispam=True,
    )
