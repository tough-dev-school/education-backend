import pytest
from functools import partial

from diplomas.services import DiplomaGenerator


@pytest.fixture(autouse=True)
def _set_diploma_generator_url(settings):
    settings.DIPLOMA_GENERATOR_HOST = 'https://secret.generator.com/'
    settings.DIPLOMA_GENERATOR_TOKEN = 'zeroc00l'


@pytest.fixture
def student(mixer):
    return mixer.blend(
        'users.User',
        first_name='Овир',
        last_name='Кривомазов',
        first_name_en='Ovir',
        last_name_en='Krivomazov',
        gender='male',
    )


@pytest.fixture
def course(mixer):
    return mixer.blend('products.Course')


@pytest.fixture(autouse=True)
def order(factory, course, student):
    return factory.order(user=student, item=course, is_paid=True)


@pytest.fixture(autouse=True)
def template(mixer, course):
    return mixer.blend('diplomas.DiplomaTemplate', slug='test-template', course=course, language='RU', homework_accepted=False)


@pytest.fixture
def generator(course, student):
    return partial(DiplomaGenerator, course=course, student=student)
