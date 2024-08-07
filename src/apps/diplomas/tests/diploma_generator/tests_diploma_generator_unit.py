import pytest

from apps.diplomas.models import DiplomaTemplate
from apps.users.models import User

pytestmark = [
    pytest.mark.django_db,
]


def test_study_object(generator, order):
    generator = generator(language="RU")

    assert generator.study == order.study, "study object is returned"


@pytest.mark.parametrize(
    ("gender", "expected"),
    [
        ("", "m"),
        (None, "m"),
        (User.GENDERS.FEMALE, "f"),
        (User.GENDERS.MALE, "m"),
    ],
)
def test_sex(generator, gender, expected):
    generator = generator(language="RU")
    generator.student.gender = gender

    template_context = generator.get_template_context()

    assert template_context["sex"] == expected


def test_user_name_ru(generator):
    generator = generator(language="RU")
    generator.student.first_name = "Авраам"
    generator.student.last_name = "Линкольн"

    template_context = generator.get_template_context()

    assert template_context["name"] == "Авраам Линкольн"


def test_user_name_en(generator):
    generator = generator(language="EN")
    generator.student.first_name_en = "Abraham"
    generator.student.last_name_en = "Lincoln"

    template_context = generator.get_template_context()

    assert template_context["name"] == "Abraham Lincoln"


def test_additional_course_context(generator, course):
    course.update(diploma_template_context={"test": "__mocked"})

    generator = generator(language="RU")

    template_context = generator.get_template_context()

    assert template_context["test"] == "__mocked"


def test_bad_language(generator):
    generator = generator(language="EN")

    with pytest.raises(DiplomaTemplate.DoesNotExist):
        generator.get_external_service_url()


def test_no_template_for_homework(generator, order):
    order.study.update(homework_accepted=True)

    generator = generator(language="RU")

    with pytest.raises(DiplomaTemplate.DoesNotExist):
        generator.get_external_service_url()


def test_external_service_url(generator, settings):
    settings.DIPLOMA_GENERATOR_HOST = "https://secret.generator.com/"

    generator = generator(language="RU")

    assert generator.get_external_service_url() == "https://secret.generator.com/test-template.png"
