import pytest

from apps.homework.services.new_answer_notifier import CrossCheckedAnswerNotification, DefaultAnswerNotification

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def mocked_default_answer_notification_can_be_sent(mocker):
    return mocker.patch(
        "apps.homework.services.new_answer_notifier.DefaultAnswerNotification.can_be_sent",
        return_value=False,
    )


@pytest.fixture(autouse=True)
def mocked_crosschecked_answer_notification_can_be_sent(mocker):
    return mocker.patch(
        "apps.homework.services.new_answer_notifier.CrossCheckedAnswerNotification.can_be_sent",
        return_value=False,
    )


def test_returns_default_notification(notifier, answer):
    notification = notifier(answer).get_notification(answer.author)

    assert isinstance(notification, DefaultAnswerNotification)


def test_returns_crosschecked_notification(notifier, answer, mocked_crosschecked_answer_notification_can_be_sent):
    mocked_crosschecked_answer_notification_can_be_sent.return_value = True

    notification = notifier(answer).get_notification(answer.author)

    assert isinstance(notification, CrossCheckedAnswerNotification)


def test_doesnt_calls_second_notification_if_first_can_be_sent(
    notifier, answer, mocked_crosschecked_answer_notification_can_be_sent, mocked_default_answer_notification_can_be_sent
):
    mocked_crosschecked_answer_notification_can_be_sent.return_value = True
    mocked_default_answer_notification_can_be_sent.return_value = True

    notifier(answer).get_notification(answer.author)

    assert not mocked_default_answer_notification_can_be_sent.called
