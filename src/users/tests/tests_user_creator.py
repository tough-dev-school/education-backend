import pytest

from users.creator import UserCreator

pytestmark = [pytest.mark.django_db]


def create(*args, **kwargs):
    return UserCreator(*args, **kwargs)()


def test():
    created = create(name='Рулон Обоев', email='rulon.oboev@gmail.com')

    created.refresh_from_db()

    assert created.first_name == 'Рулон'
    assert created.last_name == 'Обоев'
    assert created.email == 'rulon.oboev@gmail.com'


def test_default_username():
    created = create(name='Ведро Помоев', email='vedro.pomoev@gmail.com')

    assert created.username == 'vedro.pomoev@gmail.com'


def test_empty_name():
    created = create(name='', email='rulon.oboev@gmail.com')

    created.refresh_from_db()

    assert created.first_name == ''
    assert created.last_name == ''
    assert created.email == 'rulon.oboev@gmail.com'
    assert created.username == 'rulon.oboev@gmail.com'


def test_empty_email():
    created = create(name='Рулон Обоев', email='')

    created.refresh_from_db()

    assert created.first_name == 'Рулон'
    assert created.last_name == 'Обоев'
    assert created.email == ''
    assert len(created.username) > 0


def test_existing_user(user):
    created = create(name='Камаз Отходов', email=user.email)

    created.refresh_from_db()

    assert created == user


def test_existing_user_name_does_not_change(user):
    created = create(name='Камаз Отходов', email=user.email)

    created.refresh_from_db()

    assert created.first_name == user.first_name
    assert created.last_name == user.last_name
    assert created.first_name != 'Камаз'
    assert created.last_name != 'Отходов'
