import pytest

from users.creator import UserCreator

pytestmark = [pytest.mark.django_db]


def test_existing_user(user):
    created = UserCreator(name='Камаз Отходов', email='rulon.oboev@gmail.com')()

    created.refresh_from_db()

    assert created == user


def test_two_users_with_same_email(user, mixer):
    mixer.blend('users.User', email='rulon.oboev@gmail.com')
    created = UserCreator(name='Камаз Отходов', email='rulon.oboev@gmail.com')()

    created.refresh_from_db()

    assert created == user


def test_two_users_with_same_email_case_is_case_insensitive(user, mixer):
    mixer.blend('users.User', username='RULON.OBOEV@gmail.com', email='11@gmail.com')
    created = UserCreator(name='Камаз Отходов', email='rulon.oboev@gmail.com')()

    created.refresh_from_db()

    assert created == user


def test_existing_user_name_does_not_change(user):
    created = UserCreator(name='Камаз Отходов', email='rulon.oboev@gmail.com')()

    created.refresh_from_db()

    assert created.first_name == user.first_name
    assert created.last_name == user.last_name
    assert created.first_name != 'Камаз'
    assert created.last_name != 'Отходов'


@pytest.mark.parametrize('email', ['Rulon.oboev@gmail.com', 'RULON.OBOEV@GMAIL.COM'])
def test_users_with_same_email_case_insensitive(user, email):
    created = UserCreator(name='Рулон Обоев', email=email)()

    created.refresh_from_db()

    assert created == user
