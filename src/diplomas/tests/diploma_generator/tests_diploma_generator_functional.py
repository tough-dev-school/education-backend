import pytest
import requests_mock

from diplomas.models import Diploma
from diplomas.tasks import generate_diploma

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures('template'),
]


@pytest.fixture(autouse=True)
def _set_diploma_generator_url(settings):
    settings.DIPLOMA_GENERATOR_HOST = 'https://secret.generator.com/'
    settings.DIPLOMA_GENERATOR_TOKEN = 'zeroc00l'


@pytest.fixture(autouse=True)
def _mock_response():
    with requests_mock.Mocker() as http_mock:
        http_mock.get('https://secret.generator.com/test-template.png?name=%D0%9E%D0%B2%D0%B8%D1%80+%D0%9A%D1%80%D0%B8%D0%B2%D0%BE%D0%BC%D0%B0%D0%B7%D0%BE%D0%B2&sex=m', content=b'TYPICAL MAC USER JPG')
        yield


def test_service(generator, student, course):
    generator = generator(language='ru', with_homework=True)

    diploma = generator()

    assert diploma.image.read() == b'TYPICAL MAC USER JPG'
    assert diploma.study.student == student
    assert diploma.study.course == course


def test_diploma_is_regenrated_when_it_already_exists(generator, student, course):
    generator = generator(language='ru', with_homework=True)

    diploma = generator()
    diploma = generator()

    assert diploma.image.read() == b'TYPICAL MAC USER JPG'
    assert diploma.study.student == student
    assert diploma.study.course == course


def test_task(student, course):
    generate_diploma.delay(student_id=student.id, course_id=course.id, language='ru', with_homework=True)

    diploma = Diploma.objects.get(study__student=student, study__course=course)

    assert diploma.image.read() == b'TYPICAL MAC USER JPG'
    assert diploma.study.student == student
    assert diploma.study.course == course


def test_template_interface(template, student, course):
    template.generate_diploma(student)

    diploma = Diploma.objects.get(study__student=student, study__course=course)

    assert diploma.image.read() == b'TYPICAL MAC USER JPG'
    assert diploma.study.student == student
    assert diploma.study.course == course
