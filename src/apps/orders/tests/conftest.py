import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def user(mixer):
    return mixer.blend("users.User", first_name="Авраам Соломонович", last_name="Пейзенгольц")


@pytest.fixture
def course(factory):
    return factory.course(
        name="Кройка и шитьё",
        full_name="Курс кройки и шитья",
        name_genitive="Кройки и шитья",
        price=100500,
    )
