import pytest

from chains import tasks

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures('study', 'parent_message'),
]


def test_sent(send_message, parent_message, study):
    tasks.send_active_chains()

    send_message.assert_called_once_with(parent_message, to=study)


def test_inactive_chains_are_not_sent(send_message, chain):
    chain.sending_is_active = False
    chain.save()

    tasks.send_active_chains()

    send_message.assert_not_called()
