import pytest

from diplomas.models import Diploma
from diplomas.models import Languages

pytestmark = pytest.mark.django_db


@pytest.fixture
def diploma(factory):
    return factory.diploma()


@pytest.fixture
def study(factory):
    return factory.study()


@pytest.fixture
def data(image, study):
    return {
        "course": study.course.id,
        "image": image,
        "language": Languages.RU,
        "student": study.student.id,
    }


def test_ok(as_superuser, data):
    as_superuser.post("/admin/diplomas/diploma/add/", as_response=True, data=data, format="multipart")

    diploma = Diploma.objects.get()
    assert diploma.language == data["language"]
    assert diploma.study.course_id == data["course"]
    assert diploma.study.student_id == data["student"]

    assert diploma.image.file.name.startswith("/tmp/media/diplomas/")
    assert diploma.image.file.name.endswith(".gif")


def test_err_message_if_diploma_already_exists(as_superuser, data, diploma):
    data.update(course=diploma.study.course.id, language=diploma.language, student=diploma.study.student.id)

    response = as_superuser.post(
        "/admin/diplomas/diploma/add/",
        as_response=True,
        data=data,
        format="multipart",
    )

    assert f"Диплом для этого студента на языке `{diploma.language}` уже существует!" in response.content.decode()


def test_err_message_if_student_not_enrolled_in_course(as_superuser, course, data, student):
    data.update(course=course.id, student=student.id)

    response = as_superuser.post(
        "/admin/diplomas/diploma/add/",
        as_response=True,
        data=data,
        format="multipart",
    )

    assert f"Студент {student.get_full_name()} не обучался на курсе «{course.name}»!" in response.content.decode()


@pytest.mark.parametrize(
    ("field", "message"),
    [
        ("course", "Поле «Курс» — обязательное!"),
        ("image", "Поле «Обложка» — обязательное!"),
        ("language", "Поле «Язык» — обязательное!"),
        ("student", "Поле «Студент» — обязательное!"),
    ],
)
def test_err_messages_in_required_fields(as_superuser, data, field, message):
    del data[field]

    response = as_superuser.post(
        "/admin/diplomas/diploma/add/",
        as_response=True,
        data=data,
        format="multipart",
    )

    assert message in response.content.decode()
