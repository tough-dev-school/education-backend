import pytest

from app.admin import admin
from diplomas.admin import DiplomaAdmin
from diplomas.admin.forms import DiplomaAddForm
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
def data(study):
    return {
        "course": study.course.id,
        "student": study.student.id,
        "language": Languages.RU,
    }


def test_diploma_created_via_admin_class(data, study):
    form = DiplomaAddForm(data=data)

    form.is_valid()
    DiplomaAdmin(Diploma, admin.site).save_model(None, Diploma(), form, None)

    diploma = Diploma.objects.get()
    assert diploma.study == study
    assert diploma.language == data["language"]
    assert diploma.image == ""


def test_cant_validate_form_with_same_language(data, diploma):
    data = {
        "course": diploma.study.course.id,
        "student": diploma.study.student.id,
        "language": diploma.language,
    }

    form = DiplomaAddForm(data=data)

    assert not form.is_valid()
    assert (
        f"Диплом для студента {diploma.study.student.get_full_name()} курса «{diploma.study.course.name}» на языке `{diploma.language}` уже существует!"
        in form.errors["__all__"]
    )


def test_cant_validate_form_when_no_study(course, student):
    data = {
        "course": course.id,
        "student": student.id,
    }

    form = DiplomaAddForm(data=data)

    assert not form.is_valid()
    assert f"Студент {student.get_full_name()} не обучался на курсе «{course.name}»!" in form.errors["__all__"]
