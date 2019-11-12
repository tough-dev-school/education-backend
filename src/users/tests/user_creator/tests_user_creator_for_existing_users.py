import pytest

from users.creator import UserCreator

pytestmark = [pytest.mark.django_db]


def test_existing_user(user):
    created = UserCreator(name='Камаз Отходов', email=user.email)()

    created.refresh_from_db()

    assert created == user


def test_existing_user_name_does_not_change(user):
    created = UserCreator(name='Камаз Отходов', email=user.email)()

    created.refresh_from_db()

    assert created.first_name == user.first_name
    assert created.last_name == user.last_name
    assert created.first_name != 'Камаз'
    assert created.last_name != 'Отходов'
