import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("message", "progress"),
    pytest.mark.freeze_time("2032-12-01 15:30:00"),
]


def test_no_messages_are_sent(chain_sender, send_message):
    chain_sender()

    send_message.assert_not_called()


@pytest.mark.usefixtures("progress")
def test_sent_if_progress_exists(chain_sender, send_message, freezer, message, study):
    freezer.move_to("2032-12-01 15:35:00")

    chain_sender()

    send_message.assert_called_once_with(message, study=study)


@pytest.mark.usefixtures("progress")
def test_not_sent_if_time_has_not_come(chain_sender, send_message, freezer):
    freezer.move_to("2032-12-01 15:32:00")  # move 2 minutes forward when delay of message is 3 minutes

    chain_sender()

    send_message.assert_not_called()


def test_message_is_not_sent_when_it_is_already_sent(mixer, chain_sender, send_message, message, study):
    mixer.blend("chains.Progress", study=study, message=message)

    chain_sender()

    send_message.assert_not_called()
