import pytest

pytestmark = [pytest.mark.django_db]


@pytest.mark.parametrize(
    ("first_name", "last_name", "expected"),
    [
        ("Kamaz", "Othodov", "Kamaz Othodov"),
        ("Kamaz", "", "Kamaz"),
        ("", "Othodov", "Othodov"),
    ],
)
def test(mixer, first_name, last_name, expected):
    user = mixer.blend("users.User", first_name=first_name, last_name=last_name)

    assert str(user) == expected


def test_random_username_is_used_by_default(mixer):
    user = mixer.blend("users.User", first_name="", last_name="", random_name="Прилипчивый коза")

    assert str(user) == "Прилипчивый коза"


def test_anonymous_name_is_used_when_all_other_options_failed(mixer):
    user = mixer.blend("users.User", first_name="", last_name="", random_name="")

    assert str(user) == "Anonymous"
