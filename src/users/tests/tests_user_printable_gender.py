import pytest

pytestmark = [pytest.mark.django_db]


@pytest.mark.parametrize(('gender', 'expected'), [
    ('male', 'male'),
    ('female', 'female'),
    ('', 'male'),
])
def test(mixer, gender, expected):
    user = mixer.blend('users.User', gender=gender)

    assert user.get_printable_gender() == expected
