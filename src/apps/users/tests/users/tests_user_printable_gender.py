import pytest

from apps.users.models import User

pytestmark = [pytest.mark.django_db]


@pytest.mark.parametrize(
    ("gender", "expected"),
    [
        (User.GENDERS.MALE, "male"),
        (User.GENDERS.FEMALE, "female"),
        ("", "male"),
    ],
)
def test_printable_gender(mixer, gender, expected):
    user = mixer.blend("users.User", gender=gender)

    assert user.get_printable_gender() == expected
