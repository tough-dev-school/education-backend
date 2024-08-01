import pytest

pytestmark = [pytest.mark.django_db]


@pytest.mark.parametrize(
    ("first_name", "last_name", "expected"),
    [
        ("Овир", "Кривомазов", "Овир Кривомазов"),
        ("Овир", "", "Овир"),
        ("Ови", "", None),
        ("", "", None),
        ("", "Кривомазов", "Кривомазов"),
    ],
)
def test_russian(mixer, first_name, last_name, expected):
    user = mixer.blend("users.User", first_name=first_name, last_name=last_name)

    assert user.get_printable_name(language="ru") == expected


@pytest.mark.parametrize("language", ["ru", "RU"])
def test_language_spelling_is_case_insensitive(mixer, language):
    user = mixer.blend("users.User", first_name="Овир", last_name="Кривомазов")

    assert user.get_printable_name(language=language) == "Овир Кривомазов"


@pytest.mark.parametrize(
    ("first_name_en", "last_name_en", "expected"),
    [
        ("Abraham", "Lincoln", "Abraham Lincoln"),
        ("Abraham", "", "Abraham"),
        ("Ови", "", None),
        ("", "", None),
        ("", "Lincoln", "Lincoln"),
    ],
)
def test_english(mixer, first_name_en, last_name_en, expected):
    user = mixer.blend("users.User", first_name_en=first_name_en, last_name_en=last_name_en)

    assert user.get_printable_name(language="en") == expected
