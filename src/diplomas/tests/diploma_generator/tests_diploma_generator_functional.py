import pytest

from diplomas.models import Diploma
from diplomas.tasks import generate_diploma

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def _mock_response(httpx_mock):
    httpx_mock.add_response(content=b'TYPICAL MAC USER JPG')


def test_service(generator, student, course):
    generator = generator(language='ru')

    diploma = generator()

    assert diploma.image.read() == b'TYPICAL MAC USER JPG'
    assert diploma.study.student == student
    assert diploma.study.course == course


def test_diploma_is_regenrated_when_it_already_exists(generator, student, course):
    generator = generator(language='ru')

    first_diploma = generator()
    second_diploma = generator()

    assert second_diploma.slug == first_diploma.slug, 'slug should remain the same'
    assert second_diploma.image.read() == b'TYPICAL MAC USER JPG'
    assert second_diploma.study.student == student
    assert second_diploma.study.course == course


def test_task(student, course):
    generate_diploma.delay(student_id=student.id, course_id=course.id, language='ru')

    diploma = Diploma.objects.get(study__student=student, study__course=course)

    assert diploma.image.read() == b'TYPICAL MAC USER JPG'
    assert diploma.study.student == student
    assert diploma.study.course == course
