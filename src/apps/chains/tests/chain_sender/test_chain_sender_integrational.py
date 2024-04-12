import pytest

from apps.chains import tasks
from apps.chains.models import Message
from apps.users.models import User

pytestmark = [
    pytest.mark.django_db(transaction=True),
    pytest.mark.freeze_time("2032-12-01 15:30"),
]


@pytest.fixture
def owl(mocker):
    return mocker.patch("apps.mailing.tasks.Owl")


@pytest.fixture
def assert_message_is_sent(owl, study):
    def _assert(message: Message, to: User | None = None, reset: bool | None = True):
        student = to or study.student
        owl.assert_any_call(
            to=student.email,
            subject="",
            disable_antispam=False,
            template_id=message.template_id,
            ctx={
                "firstname": student.first_name,
                "lastname": student.last_name,
            },
        )

        if reset:
            owl.reset_mock()

    return _assert


@pytest.fixture
def assert_nothing_is_sent(owl):
    return owl.assert_not_called


@pytest.fixture
def another_order(factory, course, another_user):
    return factory.order(user=another_user, item=course, is_paid=True)


@pytest.fixture
def another_study(another_order):
    return another_order.study


def test(parent_message, message, assert_message_is_sent, freezer):
    tasks.send_active_chains()
    assert_message_is_sent(parent_message)  # root message is sent for the first time

    freezer.move_to("2032-12-01 15:40")  # 10 minutes forward
    tasks.send_active_chains()

    assert_message_is_sent(message)  # second message is sent


def test_two_users(parent_message, message, assert_message_is_sent, freezer, study, another_study):
    tasks.send_active_chains()

    assert_message_is_sent(parent_message, to=study.student, reset=False)
    assert_message_is_sent(parent_message, to=another_study.student)

    freezer.move_to("2032-12-01 15:40")  # 10 minutes forward
    tasks.send_active_chains()

    assert_message_is_sent(message, to=study.student, reset=False)
    assert_message_is_sent(message, to=another_study.student)


def test_second_message_is_not_sent_when_it_is_too_early(parent_message, assert_message_is_sent, assert_nothing_is_sent):
    tasks.send_active_chains()
    assert_message_is_sent(parent_message)  # root message is sent for the first time

    tasks.send_active_chains()
    assert_nothing_is_sent()  # nothing should be sent right after that, cuz time has not come


def test_message_is_not_sent_when_study_model_disappeares_during_learning(parent_message, assert_message_is_sent, assert_nothing_is_sent, freezer, order):
    tasks.send_active_chains()
    assert_message_is_sent(parent_message)  # root message is sent for the first time

    freezer.move_to("2032-12-01 15:40")  # 10 minutes forward
    order.unship()
    tasks.send_active_chains()

    assert_nothing_is_sent()  # nothing should be sent cuz student has canceled learning


def test_message_is_not_sent_when_sending_is_disabled(assert_nothing_is_sent, chain):
    chain.update(sending_is_active=False)

    tasks.send_active_chains()

    assert_nothing_is_sent()
