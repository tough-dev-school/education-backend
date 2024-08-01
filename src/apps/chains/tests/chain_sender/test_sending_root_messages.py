import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("message", "parent_message"),
]


@pytest.fixture
def second_parent_message(mixer, chain):
    return mixer.blend("chains.Message", parent=None, chain=chain)


@pytest.fixture
def another_study(mixer, course):
    return mixer.blend("studying.Study", course=course)


def test_sent(chain_sender, send_message, parent_message, study):
    chain_sender()

    send_message.assert_called_once_with(parent_message, study=study)


def test_root_message_is_only_sent_when_there_is_no_progress_record(chain_sender, send_message, parent_message, study, mixer):
    mixer.blend("chains.Progress", message=parent_message, study=study)

    chain_sender()

    send_message.assert_not_called()


def test_progress_records_from_another_studies_are_ignored(chain_sender, send_message, parent_message, study, another_study, mixer):
    mixer.blend("chains.Progress", message=parent_message, study=another_study)

    chain_sender()

    send_message.assert_called_once_with(parent_message, study=study)


def test_two_root_messages_are_sent(chain_sender, send_message, parent_message, second_parent_message, study, mocker):
    chain_sender()

    send_message.assert_has_calls(
        [
            mocker.call(parent_message, study=study),
            mocker.call(second_parent_message, study=study),
        ]
    )
