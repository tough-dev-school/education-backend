import pytest

from apps.diplomas.models import Diploma
from apps.diplomas.models import Languages

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def student(mixer):
    return mixer.blend("users.User")


@pytest.fixture(autouse=True)
def order(factory, course, student):
    return factory.order(user=student, item=course, is_paid=True)


@pytest.fixture
def image(factory):
    return factory.image()


@pytest.fixture
def payload(student, course, image):
    return {
        "student": student.id,
        "course": course.id,
        "image": image,
        "language": "RU",
    }


def test_uploading(api, payload, course, student):
    api.user.add_perm("diplomas.diploma.add_diploma")

    api.post("/api/v2/diplomas/", payload, format="multipart")

    created = Diploma.objects.last()

    assert created.study.course == course
    assert created.study.student == student
    assert created.language == Languages.RU

    assert "-4" in created.image.path
    assert created.image.path.endswith(".gif")


def test_no_anon(anon, payload):
    anon.post("/api/v2/diplomas/", payload, format="multipart", expected_status_code=401)


def test_no_perm(api, payload):
    api.post("/api/v2/diplomas/", payload, format="multipart", expected_status_code=403)
