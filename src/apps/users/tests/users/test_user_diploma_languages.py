import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def create_user(mixer):
    return lambda first_name, last_name, first_name_en, last_name_en: mixer.blend(
        "users.User",
        first_name=first_name,
        last_name=last_name,
        first_name_en=first_name_en,
        last_name_en=last_name_en,
    )


@pytest.mark.parametrize(
    ("first_name_ru", "last_name_ru", "first_name_en", "last_name_en", "expected_languages"),
    [
        ("Васятка", "Кряков", "Zeleboba", "Yakubov", {"RU", "EN"}),
        ("Васятка", "", "", "Yakubov", {"RU", "EN"}),
        ("Васятка", "Кряков", "", "", {"RU"}),
        ("", "Кряков", "", "", {"RU"}),
        ("Васятка", "", "", "", {"RU"}),
        ("", "", "Zeleboba", "Yakubov", {"EN"}),
        ("", "", "Zeleboba", "", {"EN"}),
        ("", "", "", "Yakubov", {"EN"}),
        ("", "", "", "", set()),
    ],
)
def test_diploma_languages(create_user, first_name_ru, last_name_ru, first_name_en, last_name_en, expected_languages):
    user = create_user(first_name_ru, last_name_ru, first_name_en, last_name_en)

    assert user.diploma_languages == expected_languages
