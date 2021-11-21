import pytest
from django.core import management
from pytest_mock import MockerFixture

pytestmark = pytest.mark.django_db


@pytest.fixture
def handle_single_email_mock(mocker: MockerFixture):
    return mocker.patch('users.management.commands.merge_same_email_users.Command.handle_single_email')


def test_command_handles_single_account_email(bob_a, handle_single_email_mock):
    management.call_command('merge_same_email_users')

    handle_single_email_mock.assert_called_once_with('boB@EXAMPLE.com')


def test_command_handles_every_user_email(bob_a, bob_b, bob_c, handle_single_email_mock, mocker):
    management.call_command('merge_same_email_users')

    handle_single_email_mock.assert_has_calls((
        mocker.call('boB@EXAMPLE.com'),
        mocker.call('Bob@Example.Com'),
        mocker.call('BOB@EXAMPLE.COM'),
    ), any_order=True)


def test_command_doesnt_handle_disabled_accounts(mixer, bob_a, handle_single_email_mock):
    mixer.blend('users.User', email='alice@example.com', is_active=False)

    management.call_command('merge_same_email_users')

    handle_single_email_mock.assert_called_once_with('boB@EXAMPLE.com')
