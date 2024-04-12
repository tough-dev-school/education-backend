import pytest

from apps.chains import tasks

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("study", "parent_message"),
]


def test_sent(send_message, parent_message, study):
    tasks.send_active_chains()

    send_message.assert_called_once_with(parent_message, study=study)


def test_sending_inactive_chains_are_not_sent(send_message, chain):
    chain.update(sending_is_active=False)

    tasks.send_active_chains()

    send_message.assert_not_called()


def test_archived_chains_are_not_sent(send_message, chain):
    chain.update(archived=True)

    tasks.send_active_chains()

    send_message.assert_not_called()
