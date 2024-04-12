import pytest
from respx import MockRouter

from apps.diplomas.models import Diploma
from apps.diplomas.tasks import generate_diploma

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def _mock_response(respx_mock: MockRouter):
    respx_mock.route().respond(content=b"TYPICAL MAC USER JPG")


def test_service(generator, student, course):
    generator = generator(language="RU")

    diploma = generator()

    assert diploma.image.read() == b"TYPICAL MAC USER JPG"
    assert diploma.study.student == student
    assert diploma.study.course == course


def test_diploma_is_regenerated_when_it_already_exists(generator, student, course):
    generator = generator(language="RU")

    first_diploma = generator()
    second_diploma = generator()

    assert second_diploma.slug == first_diploma.slug, "slug should remain the same"
    assert second_diploma.image.read() == b"TYPICAL MAC USER JPG"
    assert second_diploma.study.student == student
    assert second_diploma.study.course == course


def test_task(student, course):
    generate_diploma.delay(student_id=student.id, course_id=course.id, language="RU")

    diploma = Diploma.objects.get(study__student=student, study__course=course)

    assert diploma.image.read() == b"TYPICAL MAC USER JPG"
    assert diploma.study.student == student
    assert diploma.study.course == course
