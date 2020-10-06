import pytest

from users.models import User

pytestmark = [pytest.mark.django_db]


@pytest.mark.parametrize('name, parsed', [
    ['Камаз', {'first_name': 'Камаз'}],
    ['Камаз Отходов', {'first_name': 'Камаз', 'last_name': 'Отходов'}],
    ['Камаз Отходов Петрович', {'first_name': 'Камаз', 'last_name': 'Отходов Петрович'}],
    ['', {'first_name': ''}],
    [None, {}],
])
def test(name, parsed):
    assert User.parse_name(name) == parsed
