import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def course(factory):
    return factory.course(name="Упячивание бутявок", name_genitive="Упячивания бутявок")


@pytest.fixture
def record(course, factory):
    return factory.record(course=course)


def test(record):
    assert "Запись" in str(record)
    assert "Упячивания бутявок" in str(record)
