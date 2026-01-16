import pytest

pytestmark = [pytest.mark.django_db]


@pytest.mark.parametrize(
    ["first_name", "last_name", "expected"],
    [
        ("Иванов", "Иван", "Иванову Ивану"),
        ("Иванова", "Анна", "Иванове Анне"),
    ],
)
def test(user, first_name, last_name, expected):
    user.update(first_name=first_name, last_name=last_name)

    assert user.get_printable_dative_name() == expected
