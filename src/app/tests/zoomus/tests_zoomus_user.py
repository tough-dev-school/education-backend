import pytest

from app.zoomus.user import ZoomusUser

pytestmark = [pytest.mark.django_db]


def test_default(user):
    formatted = ZoomusUser(user)

    assert formatted.first_name == 'Авраам'
    assert formatted.last_name == 'Пейзенгольц'
    assert formatted.email == 'abrakham@mail.ru'


def test_as_dict(user):
    formatted = dict(ZoomusUser(user))

    assert formatted == {
        'first_name': 'Авраам',
        'last_name': 'Пейзенгольц',
        'email': 'abrakham@mail.ru',
    }


@pytest.mark.parametrize('param', ['first_name', 'last_name'])
def test_empty_param(user, param):
    setattr(user, param, '')

    formatted = ZoomusUser(user)

    assert getattr(formatted, param) == ' '
