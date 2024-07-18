import pytest

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def mocked_default_answer_notification_send_if_should(mocker):
    return mocker.patch(
        "apps.homework.services.new_answer_notifier.DefaultAnswerNotification.send_if_should",
        return_value=True,
    )


@pytest.fixture(autouse=True)
def mocked_crosschecked_answer_notification_send_if_should(mocker):
    return mocker.patch(
        "apps.homework.services.new_answer_notifier.CrossCheckedAnswerNotification.send_if_should",
        return_value=False,
    )


def test_sends_crosschecked_answer_notification(
    notifier, parent_of_another_answer, mocked_crosschecked_answer_notification_send_if_should, mocked_default_answer_notification_send_if_should
):
    mocked_crosschecked_answer_notification_send_if_should.return_value = True

    notifier(parent_of_another_answer)()

    mocked_crosschecked_answer_notification_send_if_should.assert_called_once()
    assert not mocked_default_answer_notification_send_if_should.called


def test_calls_default_notification_if_crosschecked_not_sent(
    notifier, parent_of_another_answer, mocked_crosschecked_answer_notification_send_if_should, mocked_default_answer_notification_send_if_should
):
    mocked_crosschecked_answer_notification_send_if_should.return_value = False

    notifier(parent_of_another_answer)()

    mocked_default_answer_notification_send_if_should.assert_called_once()
