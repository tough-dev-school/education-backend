import pytest
from django.contrib.admin.models import CHANGE, LogEntry
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("_set_current_user"),
]


@pytest.fixture
def existing_user(mixer):
    return mixer.blend("users.User", email="new@email.com")


@pytest.fixture
def answer(mixer, user):
    return mixer.blend("homework.Answer", author=user)


@pytest.fixture
def order(factory, user):
    return factory.order(user=user, is_paid=True)


def test_order_data_is_migrated(service, order, user, existing_user):
    """Large test for chahnging user data"""
    assert order.user == user
    assert order.study.student == user

    service(new_email="new@email.com")()
    order.refresh_from_db()

    assert order.author == user, "author should remain unchanged"
    assert order.user == existing_user
    assert order.study.student == existing_user


def test_destination_user_order_data_remains_the_same(service, order, existing_user):
    order.update(user=existing_user)
    order.study.update(student=existing_user)

    service(new_email="new@email.com")()
    order.refresh_from_db()

    assert order.user == existing_user
    assert order.study.student == existing_user


def test_answers_are_migrated(service, answer, user, existing_user):
    assert answer.author == user

    service(new_email="new@email.com")()
    answer.refresh_from_db()

    assert answer.author == existing_user


def test_changing_to_the_course_where_user_already_existst(service, order, existing_user, factory):
    """Hope we will not encounter this issue in the real world, but i've createed some logic for developers, it should be tested as well as the user-facing"""
    factory.order(user=existing_user, item=order.course, is_paid=True)  # order with the same course

    with pytest.raises(ValidationError):
        service(new_email="new@email.com")()


def test_destination_user_answers_remains_the_same(service, answer, existing_user):
    answer.update(author=existing_user)

    service(new_email="new@email.com")()
    answer.refresh_from_db()

    assert answer.author == existing_user


@pytest.mark.auditlog
def test_auditlog_is_created_for_the_source_user(service, user, existing_user):
    service(new_email="new@email.com")()

    log = LogEntry.objects.filter(
        content_type=ContentType.objects.get_for_model(user).id,
        object_id=user.id,
    ).last()

    assert log.action_flag == CHANGE
    assert log.user == user, "mocked actor, accidently matches the user"
    assert f"#{existing_user.pk}" in log.change_message


@pytest.mark.auditlog
def test_auditlog_is_created_for_the_destination_user(service, user, existing_user):
    service(new_email="new@email.com")()

    log = LogEntry.objects.filter(
        content_type=ContentType.objects.get_for_model(user).id,
        object_id=existing_user.id,
    ).last()

    assert log.action_flag == CHANGE
    assert log.user == user, "mocked actor, accidently matches the user"
    assert f"#{user.pk}" in log.change_message
