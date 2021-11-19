import pytest
from pytest_mock import MockerFixture

pytestmark = pytest.mark.django_db


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
        mocker.call(bob_b, bob_c),
        mocker.call(bob_a, bob_c),
    ))
