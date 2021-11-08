from datetime import datetime

import pytest
from django.core import management
from mixer.backend.django import mixer
from pytest_mock import MockerFixture

from users.management.commands import merge_same_email_users
from users.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def bob_a() -> User:
    return mixer.blend('users.User', username='boB@EXAMPLE.com', email='boB@EXAMPLE.com', date_joined=datetime(2021, 11, 1))


@pytest.fixture
def bob_b() -> User:
    return mixer.blend('users.User', username='Bob@Example.Com', email='Bob@Example.Com', date_joined=datetime(2021, 11, 2))


@pytest.fixture
def bob_c() -> User:
    return mixer.blend('users.User', username='BOB@EXAMPLE.COM', email='BOB@EXAMPLE.COM', date_joined=datetime(2021, 11, 3))


@pytest.fixture
def command():
    return merge_same_email_users.Command()


@pytest.fixture
def handle_single_email_mock(mocker: MockerFixture):
    return mocker.patch('users.management.commands.merge_same_email_users.Command.handle_single_email')


#
# TEST USER MERGE
#


def test_merged_user_becomes_inactive(bob_a, bob_b, command):
    command.merge_user(source=bob_a, target=bob_b)
    assert not bob_a.is_active


def test_merged_user_changes_username_to_uuid(bob_a, bob_b, command):
    command.merge_user(source=bob_a, target=bob_b)
    assert bob_a.username == bob_a.uuid


@pytest.mark.parametrize('prop_name,prop_value,empty_value', [
    ('first_name', 'Боб', ''),
    ('last_name', 'Бобов', ''),
    ('first_name_en', 'Bob', ''),
    ('last_name_en', 'McBob', ''),
    ('subscribed', True, False),
    ('gender', 'male', '')
])
def test_target_user_populates_empty_property(bob_a, bob_b, command, prop_name, prop_value, empty_value):
    setattr(bob_a, prop_name, prop_value)
    bob_a.save()
    setattr(bob_b, prop_name, empty_value)
    bob_b.save()

    command.merge_user(source=bob_a, target=bob_b)

    assert getattr(bob_b, prop_name) == prop_value


@pytest.mark.parametrize('prop_name,prop_value,empty_value', [
    ('first_name', 'Боб', ''),
    ('last_name', 'Бобов', ''),
    ('first_name_en', 'Bob', ''),
    ('last_name_en', 'McBob', ''),
    ('subscribed', True, False),
    ('gender', 'male', '')
])
def test_target_user_preserves_non_empty_property(bob_a, bob_b, command, prop_name, prop_value, empty_value):
    setattr(bob_a, prop_name, empty_value)
    bob_a.save()
    setattr(bob_b, prop_name, prop_value)
    bob_b.save()

    command.merge_user(source=bob_a, target=bob_b)

    assert getattr(bob_b, prop_name) == prop_value


@pytest.mark.parametrize('model,rel_name', [
    ('a12n.PasswordlessAuthToken', 'user'),
    ('homework.Answer', 'author'),
    ('homework.AnswerAccessLogEntry', 'user'),
    ('homework.AnswerCrossCheck', 'checker'),
    ('magnets.LeadCampaignLogEntry', 'user'),
    ('orders.Order', 'user'),
    ('orders.Order', 'giver'),
    ('studying.Study', 'student')
])
def test_source_user_relation_merged_into_target_user(bob_a, bob_b, command, model, rel_name):
    bob_a_rel = mixer.blend(model, **{rel_name: bob_a})
    command.merge_user(bob_a, bob_b)
    bob_a_rel.refresh_from_db()
    assert getattr(bob_a_rel, rel_name) == bob_b


def test_source_user_preserves_duplicated_relation_answer_access_log_entry(bob_a, bob_b, command):
    answer = mixer.blend('homework.Answer')
    rel_a = mixer.blend('homework.AnswerAccessLogEntry', user=bob_a, answer=answer)
    rel_b = mixer.blend('homework.AnswerAccessLogEntry', user=bob_b, answer=answer)

    command.merge_user(source=bob_a, target=bob_b)

    rel_a.refresh_from_db()
    assert rel_a.user == bob_a

    rel_b.refresh_from_db()
    assert rel_b.user == bob_b


def test_source_user_preserves_duplicated_relation_answer_cross_check(bob_a, bob_b, command):
    answer = mixer.blend('homework.Answer')
    rel_a = mixer.blend('homework.AnswerCrossCheck', checker=bob_a, answer=answer)
    rel_b = mixer.blend('homework.AnswerCrossCheck', checker=bob_b, answer=answer)

    command.merge_user(source=bob_a, target=bob_b)

    rel_a.refresh_from_db()
    assert rel_a.checker == bob_a

    rel_b.refresh_from_db()
    assert rel_b.checker == bob_b


def test_source_user_preserves_duplicated_relation_study(bob_a, bob_b, command):
    course = mixer.blend('products.Course')
    rel_a = mixer.blend('studying.Study', student=bob_a, course=course)
    rel_b = mixer.blend('studying.Study', student=bob_b, course=course)

    command.merge_user(source=bob_a, target=bob_b)

    rel_a.refresh_from_db()
    assert rel_a.student == bob_a

    rel_b.refresh_from_db()
    assert rel_b.student == bob_b


@pytest.mark.parametrize('rel_model,rel_name,constraints', [
    ('studying.Study', 'student', {'course': 'products.Course'}),
    ('homework.AnswerCrossCheck', 'checker', {'answer': 'homework.Answer'}),
    ('homework.AnswerAccessLogEntry', 'user', {'answer': 'homework.Answer'}),
])
def test_source_user_preserves_duplicated_relations(bob_a, bob_b, command, rel_model, rel_name, constraints):
    """Parametrized version of 3 tests above, written for comparison"""
    for k, v in constraints.items():
        constraints[k] = mixer.blend(v)

    rel_a = mixer.blend(rel_model, **{rel_name: bob_a}, **constraints)
    rel_b = mixer.blend(rel_model, **{rel_name: bob_b}, **constraints)

    command.merge_user(source=bob_a, target=bob_b)

    rel_a.refresh_from_db()
    assert getattr(rel_a, rel_name) == bob_a

    rel_b.refresh_from_db()
    assert getattr(rel_b, rel_name) == bob_b


#
# TEST SINGLE EMAIL MERGE
#

def test_target_user_lower_email(bob_a, bob_b, command, mocker: MockerFixture):
    command.merge_user = mocker.MagicMock()
    command.handle_single_email(bob_a.email)
    bob_b.refresh_from_db()
    assert bob_b.email == bob_b.email.lower()


def test_target_user_lower_username(bob_a, bob_b, command, mocker: MockerFixture):
    command.merge_user = mocker.MagicMock()
    command.handle_single_email(bob_a.email)
    bob_b.refresh_from_db()
    assert bob_b.username == bob_b.username.lower()


def test_two_users_merge_into_latest(bob_a, bob_b, command, mocker: MockerFixture):
    command.merge_user = mocker.MagicMock()
    command.handle_single_email(bob_a.email)
    command.merge_user.assert_called_once_with(bob_a, bob_b)


def test_three_users_merge_into_latest(bob_a, bob_b, bob_c, command, mocker: MockerFixture):
    command.merge_user = mocker.MagicMock()
    command.handle_single_email(bob_a.email)
    command.merge_user.assert_has_calls((
        mocker.call(bob_b, bob_a),
        mocker.call(bob_c, bob_a)
    ))


#
# TEST WHOLE COMMAND
#

def test_command_handles_email_case_insensitive(bob_a, bob_b, bob_c, handle_single_email_mock):
    management.call_command('merge_same_email_users')
    handle_single_email_mock.assert_called_once_with('bob@example.com')


def test_command_handles_single_account_email(bob_a, handle_single_email_mock):
    management.call_command('merge_same_email_users')
    handle_single_email_mock.assert_called_once_with('bob@example.com')


def test_command_doesnt_handle_disabled_accounts(bob_a, handle_single_email_mock):
    mixer.blend('users.User', email='alice@gmail.com', is_active=False)
    management.call_command('merge_same_email_users')
    handle_single_email_mock.assert_called_once_with('bob@example.com')
