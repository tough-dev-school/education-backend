import pytest

from users.creator import UserCreator

pytestmark = [pytest.mark.django_db]


def test():
    created = UserCreator(name='Рулон Обоев', email='rulon.oboev@gmail.com')()

    created.refresh_from_db()

    assert created.first_name == 'Рулон'
    assert created.last_name == 'Обоев'
    assert created.email == 'rulon.oboev@gmail.com'


def test_default_username():
    created = UserCreator(name='Ведро Помоев', email='vedro.pomoev@gmail.com')()

    assert created.username == 'vedro.pomoev@gmail.com'


@pytest.mark.parametrize('name', ['', None])
def test_empty_name(name):
    created = UserCreator(name=name, email='rulon.oboev@gmail.com')()

    created.refresh_from_db()

    assert created.first_name == ''
    assert created.last_name == ''
    assert created.email == 'rulon.oboev@gmail.com'
    assert created.username == 'rulon.oboev@gmail.com'


def test_empty_email():
    created = UserCreator(name='Рулон Обоев', email='')()

    created.refresh_from_db()

    assert created.first_name == 'Рулон'
    assert created.last_name == 'Обоев'
    assert created.email == ''
    assert len(created.username) > 0
