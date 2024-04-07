import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def course(factory):
    return factory.course(name="Кройка и шитьё", name_genitive="Кройки и шитья")
