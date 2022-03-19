import pytest

from chains import tasks
from chains.models import Message

pytestmark = [
    pytest.mark.django_db(transaction=True),
    pytest.mark.freeze_time('2032-12-01 15:30'),
]


@pytest.fixture
def owl(mocker):
    return mocker.patch('app.tasks.mail.TemplOwl')


@pytest.fixture
def assert_message_is_sent(owl, study):
    def _assert(message: Message):
        owl.assert_called_once_with(
            to=study.student.email,
            subject='',
            disable_antispam=False,
            template_id=message.template_id,
            ctx={
                'firstname': study.student.first_name,
                'lastname': study.student.last_name,
            },
        )

        owl.reset_mock()

    return _assert


@pytest.fixture
def assert_nothing_is_sent(owl):
    return owl.assert_not_called


def test(study, parent_message, message, assert_message_is_sent, assert_nothing_is_sent, freezer):
    tasks.send_active_chains()
    assert_message_is_sent(parent_message)  # root message is sent for the first time

    tasks.send_active_chains()
    assert_nothing_is_sent()  # nothing should be sent right after that

    freezer.move_to('2032-12-01 15:40')  # 10 minutes forward

    tasks.send_active_chains()
    assert_message_is_sent(message)  # second message is sent


def test_message_is_not_sent_when_study_model_disappeares_during_learning(study, parent_message, assert_message_is_sent, assert_nothing_is_sent, freezer, order):
    tasks.send_active_chains()
    assert_message_is_sent(parent_message)  # root message is sent for the first time

    freezer.move_to('2032-12-01 15:40')  # 10 minutes forward
    order.unship()
    tasks.send_active_chains()

    assert_nothing_is_sent()  # nothing should be sent cuz student has canceled learning
