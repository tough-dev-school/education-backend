import pytest
import re

from apps.diplomas.admin import DiplomaForm
from apps.diplomas.models import Diploma
from apps.diplomas.models import Languages

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

    assert "Такой диплом уже создан, попробуйте выбрать другой язык." in response.content.decode()


def test_err_message_if_student_not_enrolled_in_course(as_superuser, course, data, student):
    data.update(course=course.id, student=student.id)

    response = as_superuser.post(
        "/admin/diplomas/diploma/add/",
        as_response=True,
        data=data,
        format="multipart",
    )

    assert "Выбранный студент не учился на этом курсе." in response.content.decode()


def test_required_field_messages_shown_when_fields_not_set(as_superuser, subtests):
    response = as_superuser.post(
        "/admin/diplomas/diploma/add/",
        as_response=True,
        data={},
        format="multipart",
    )

    for fieldname in DiplomaForm().required_fields:
        with subtests.test(fieldname=fieldname):
            assert re.search(
                rf'<div class="form-row errors field-{fieldname}">\s+<ul class="errorlist"><li>Обязательное поле.</li></ul>',
                response.content.decode(),
            )
