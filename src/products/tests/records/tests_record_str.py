import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def course(mixer):
    return mixer.blend('products.Course', name='Упячивание бутявок', name_genitive='Упячивания бутявок')


@pytest.fixture
def record(course, mixer):
    return mixer.blend('products.Record', course=course)


def test(record):
    assert 'Запись' in str(record)
    assert 'Упячивания бутявок' in str(record)
