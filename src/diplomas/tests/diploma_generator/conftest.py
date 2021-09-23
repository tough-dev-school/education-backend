import pytest
from functools import partial

from diplomas.services import DiplomaGenerator


@pytest.fixture
def student(mixer):
    return mixer.blend('users.User', first_name='Овир', last_name='Кривомазов', gender='male')


@pytest.fixture
def course(mixer):
    return mixer.blend('products.Course')


@pytest.fixture
def order(factory, course, student):
    return factory.order(user=student, item=course, is_paid=True)


@pytest.fixture
def template(mixer, course):
    return mixer.blend('diplomas.DiplomaTemplate', slug='test-template', course=course, language='ru')


@pytest.fixture
def generator(course, student):
    return partial(DiplomaGenerator, course=course, student=student)
