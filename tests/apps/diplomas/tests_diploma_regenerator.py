import pytest

from apps.diplomas import tasks
from apps.diplomas.models import Diploma
from apps.diplomas.models import Languages
from apps.diplomas.services import DiplomaGenerator
from apps.diplomas.services import DiplomaRegenerator

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def _mock_diploma_generator_fetch_image(mocker, factory):
    image = factory.image()
    mocker.patch("apps.diplomas.services.diploma_regenerator.DiplomaGenerator.fetch_image", return_value=image)


@pytest.fixture(autouse=True)
def template_en(mixer, course):
    return mixer.blend(
        "diplomas.DiplomaTemplate",
        slug="test-template",
        course=course,
        language=Languages.EN,
        homework_accepted=False,
    )


@pytest.fixture
def diploma_ru(mixer, order):
    return mixer.blend("diplomas.Diploma", study=order.study, language=Languages.RU)


@pytest.fixture
def diploma_en(mixer, order):
    return mixer.blend("diplomas.Diploma", study=order.study, language=Languages.EN)


@pytest.fixture
def mock_diploma_generator(mocker):
    return mocker.patch("apps.diplomas.services.diploma_generator.DiplomaGenerator.__call__", autospec=True)


@pytest.fixture
def mock_diploma_regenerator(mocker):
    return mocker.patch("apps.diplomas.services.diploma_regenerator.DiplomaRegenerator.__call__", autospec=True)


@pytest.fixture
def student_without_english_name(student):
    return student.update(first_name_en="", last_name_en="")


def test_diplomas_are_regenerated(student, diploma_ru, diploma_en, order):
    DiplomaRegenerator(student)()

    diploma_ru.refresh_from_db()
    diploma_en.refresh_from_db()
    assert diploma_ru.modified is not None
    assert diploma_en.modified is not None


def test_task_diplomas_regenerated(student, course, order, diploma_ru, diploma_en):
    tasks.regenerate_diplomas.delay(student_id=student.id)

    diploma_ru.refresh_from_db()
    diploma_en.refresh_from_db()
    assert diploma_ru.modified is not None
    assert diploma_en.modified is not None


def test_email_is_sent(send_mail, student, diploma_ru):
    DiplomaRegenerator(student)()

    send_mail.assert_called_once_with(
        to=student.email,
        template_id="diplomas_regenerated",
        disable_antispam=True,
    )


def test_task_call_regenerator(student, course, order, diploma_ru, mock_diploma_regenerator):
    tasks.regenerate_diplomas.delay(student_id=student.id)

    mock_diploma_regenerator.assert_called_once()
    called_service = mock_diploma_regenerator.call_args.args[0]
    assert called_service.student == student


@pytest.mark.usefixtures("diploma_ru", "diploma_en")
def test_diploma_generator_service_is_called(student, course, mock_diploma_generator, mocker):
    DiplomaRegenerator(student)()

    mock_diploma_generator.assert_has_calls(
        (
            mocker.call(DiplomaGenerator(course=course, student=student, language="EN")),
            mocker.call(DiplomaGenerator(course=course, student=student, language="RU")),
        ),
        any_order=True,
    )


def test_no_diplomas_are_generated_when_there_are_no_diplomas_for_user(another_user, send_mail):
    DiplomaRegenerator(another_user)()

    assert Diploma.objects.count() == 0
    send_mail.assert_not_called()


@pytest.mark.usefixtures("diploma_ru")
def test_generate_new_diplomas_in_other_languages(student):
    DiplomaRegenerator(student)()

    diplomas_en_language = Diploma.objects.filter(language=Languages.EN)
    assert diplomas_en_language.exists() is True


@pytest.mark.usefixtures("diploma_ru")
def test_do_not_generate_new_diplomas_in_other_languages_for_student_without_name_in_that_languages(student_without_english_name):
    DiplomaRegenerator(student_without_english_name)()

    diplomas_en_language = Diploma.objects.filter(language=Languages.EN)
    assert diplomas_en_language.exists() is False


@pytest.mark.usefixtures("diploma_ru")
def test_do_not_generate_new_diplomas_in_other_languages_when_no_template_in_that_languages(student, template_en):
    template_en.delete()

    DiplomaRegenerator(student)()

    diplomas_en_language = Diploma.objects.filter(language=Languages.EN)
    assert diplomas_en_language.exists() is False


@pytest.mark.usefixtures("diploma_ru")
def test_do_not_update_diplomas_in_languages_for_student_without_name_in_that_languages(student_without_english_name, diploma_en):
    DiplomaRegenerator(student_without_english_name)()

    diploma_en.refresh_from_db()
    assert diploma_en.modified is None


@pytest.mark.usefixtures("diploma_ru")
def test_do_not_update_diplomas_in_languages_when_no_template_in_that_languages(student, template_en, diploma_en):
    template_en.delete()

    DiplomaRegenerator(student)()

    diploma_en.refresh_from_db()
    assert diploma_en.modified is None


@pytest.mark.usefixtures("diploma_ru", "diploma_en")
def test_do_not_generate_new_diplomas_for_study_without_at_least_one_diploma(factory, student, send_mail):
    order = factory.order(item=factory.course(), user=student, is_paid=True)  # study for order created

    DiplomaRegenerator(student)()

    new_diplomas = Diploma.objects.filter(study=order.study)
    assert new_diplomas.exists() is False
    send_mail.assert_called_once()  # already existed diplomas were regenerated
