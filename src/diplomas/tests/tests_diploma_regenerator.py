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


def test_diplomas_are_regenerated(student, course, diploma_ru, diploma_en, order):
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


def test_task_call_regenerator(student, course, order, diploma_ru, mock_diploma_regenerator):
    tasks.regenerate_diplomas.delay(student_id=student.id)

    mock_diploma_regenerator.assert_called_once()
    called_service = mock_diploma_regenerator.call_args.args[0]
    assert called_service.student == student


def test_do_nothing_if_no_template_for_generated_diploma(student, template, diploma_ru, send_mail):
    template.delete()

    DiplomaRegenerator(student)()

    diploma_ru.refresh_from_db()
    assert diploma_ru.modified is None
    send_mail.assert_not_called()


def test_email_is_sent(send_mail, student, diploma_ru, diploma_en):
    DiplomaRegenerator(student)()

    send_mail.assert_called_once_with(
        to=student.email,
        template_id='diplomas_regenerated',
        disable_antispam=True,
    )


def test_diploma_generator_service_is_called(student, course, diploma_ru, mock_diploma_generator):
    DiplomaRegenerator(student)()

    mock_diploma_generator.assert_called()
    called_service = mock_diploma_generator.call_args.args[0]
    assert called_service.course == course
    assert called_service.student == student
    assert called_service.language == Languages.RU


def test_no_diplomas_are_generated_when_there_are_no_diplomas_for_user(another_user, send_mail):
    DiplomaRegenerator(another_user)()

    assert Diploma.objects.count() == 0
    send_mail.assert_not_called()
