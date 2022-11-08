import pytest

from diplomas import tasks
from diplomas.models import Diploma, Languages
from diplomas.services import DiplomaRegenerator

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def _mock_diploma_generator_fetch_image(mocker, factory):
    image = factory.uploaded_image()
    mocker.patch('diplomas.services.diploma_regenerator.DiplomaGenerator.fetch_image', return_value=image)


@pytest.fixture(autouse=True)
def template_en(mixer, course):
    return mixer.blend(
        'diplomas.DiplomaTemplate',
        slug='test-template',
        course=course,
        language=Languages.EN,
        homework_accepted=False,
    )


@pytest.fixture
def diploma_ru(mixer, order):
    return mixer.blend('diplomas.Diploma', study=order.study, language=Languages.RU)


@pytest.fixture
def diploma_en(mixer, order):
    return mixer.blend('diplomas.Diploma', study=order.study, language=Languages.EN)


@pytest.fixture
def mock_diploma_generator(mocker):
    return mocker.patch('diplomas.services.diploma_generator.DiplomaGenerator.__call__', autospec=True)


@pytest.fixture
def mock_diploma_regenerator(mocker):
    return mocker.patch('diplomas.services.diploma_regenerator.DiplomaRegenerator.__call__', autospec=True)


@pytest.fixture
def _remove_student_en_name(student):
    student.first_name_en = ''
    student.last_name_en = ''
    student.save()


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
        template_id='diplomas_regenerated',
        disable_antispam=True,
    )


def test_task_call_regenerator(student, course, order, diploma_ru, mock_diploma_regenerator):
    tasks.regenerate_diplomas.delay(student_id=student.id)

    mock_diploma_regenerator.assert_called_once()
    called_service = mock_diploma_regenerator.call_args.args[0]
    assert called_service.student == student


def test_call_diploma_generator_service(student, course, diploma_ru, diploma_en, mock_diploma_generator):
    DiplomaRegenerator(student)()

    first_called_service = mock_diploma_generator.call_args.args[0]
    second_called_service = mock_diploma_generator.call_args.args[1]
    assert mock_diploma_generator.call_count == 2
    assert first_called_service.course == course
    assert first_called_service.student == student
    assert first_called_service.language == Languages.RU
    assert second_called_service.course == course
    assert second_called_service.student == student
    assert second_called_service.language == Languages.EN


@pytest.mark.usefixtures('diploma_ru')
def test_generate_new_diplomas_in_other_languages(student):
    DiplomaRegenerator(student)()

    diplomas_en_language = Diploma.objects.filter(language=Languages.EN)
    assert diplomas_en_language.exists() is True


@pytest.mark.usefixtures('diploma_ru', '_remove_student_en_name')
def test_do_not_generate_new_diplomas_in_other_languages_when_no_name_in_language(student):
    DiplomaRegenerator(student)()

    diplomas_en_language = Diploma.objects.filter(language=Languages.EN)
    assert diplomas_en_language.exists() is False


@pytest.mark.usefixtures('diploma_ru')
def test_do_not_generate_new_diplomas_in_other_languages_when_no_template_in_language(student, template_en):
    template_en.delete()

    DiplomaRegenerator(student)()

    diplomas_en_language = Diploma.objects.filter(language=Languages.EN)
    assert diplomas_en_language.exists() is False


@pytest.mark.usefixtures('diploma_ru', '_remove_student_en_name')
def test_do_not_update_diplomas_in_language_when_no_name_in_language(student, diploma_en):
    DiplomaRegenerator(student)()

    diploma_en.refresh_from_db()
    assert diploma_en.modified is None


@pytest.mark.usefixtures('diploma_ru')
def test_do_not_update_diplomas_in_languages_when_no_template_in_language(student, template_en, diploma_en):
    template_en.delete()

    DiplomaRegenerator(student)()

    diploma_en.refresh_from_db()
    assert diploma_en.modified is None


def test_generate_new_diplomas_for_order_if_at_least_one_diploma_for_order_exists(another_user, send_mail):
    DiplomaRegenerator(another_user)()

    assert Diploma.objects.count() == 0
    send_mail.assert_not_called()
