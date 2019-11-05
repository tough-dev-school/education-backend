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


def test_empty_name():
    created = create(name='', email='rulon.oboev@gmail.com')

    created.refresh_from_db()

    assert created.first_name == ''
    assert created.last_name == ''
    assert created.email == 'rulon.oboev@gmail.com'


def test_empty_email():
    created = create(name='Рулон Обоев', email='')

    created.refresh_from_db()

    assert created.first_name == 'Рулон'
    assert created.last_name == 'Обоев'
    assert created.email == ''
