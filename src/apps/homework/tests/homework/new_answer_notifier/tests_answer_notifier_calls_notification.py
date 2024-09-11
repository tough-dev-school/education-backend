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


@pytest.mark.usefixtures("parent_of_another_answer")
def test_sends_crosschecked_answer_notification(
    notifier, another_answer, mocked_crosschecked_answer_notification_send_if_should, mocked_default_answer_notification_send_if_should
):
    mocked_crosschecked_answer_notification_send_if_should.return_value = True

    notifier(another_answer)()

    mocked_crosschecked_answer_notification_send_if_should.assert_called_once()
    assert not mocked_default_answer_notification_send_if_should.called


@pytest.mark.usefixtures("parent_of_another_answer")
def test_calls_default_notification_if_crosschecked_not_sent(
    notifier, another_answer, mocked_crosschecked_answer_notification_send_if_should, mocked_default_answer_notification_send_if_should
):
    mocked_crosschecked_answer_notification_send_if_should.return_value = False

    notifier(another_answer)()

    mocked_default_answer_notification_send_if_should.assert_called_once()
