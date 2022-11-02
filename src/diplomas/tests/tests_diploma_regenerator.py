import pytest

from diplomas import tasks
from diplomas.models import DiplomaTemplate
from diplomas.services import DiplomaRegenerator

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def template_en(mixer, course):
    return mixer.blend('diplomas.DiplomaTemplate', slug='test-template-en', course=course, language='EN', homework_accepted=False)


@pytest.fixture(autouse=True)
def diploma_ru(mixer, order):
    return mixer.blend('diplomas.Diploma', study=order.study, language='RU')


@pytest.fixture(autouse=True)
def diploma_en(mixer, order):
    return mixer.blend('diplomas.Diploma', study=order.study, language='EN')


@pytest.fixture(autouse=True)
def mock_diploma_generator(mocker):
    return mocker.patch('diplomas.services.diploma_regenerator.DiplomaGenerator.__init__', return_value=None)


@pytest.fixture(autouse=True)
def mock_run_diploma_generation(mocker):
    return mocker.patch('diplomas.services.diploma_generator.DiplomaGenerator.__call__')


@pytest.fixture
def mock_send_mail(mocker):
    return mocker.patch('mailing.tasks.send_mail.delay')


def test_diplomas_are_regenerated(student, course, mock_diploma_generator, mocker):
    DiplomaRegenerator(student)()

    mock_diploma_generator.assert_has_calls((
        mocker.call(course=course, student=student, language='RU'),
        mocker.call(course=course, student=student, language='EN'),
    ), any_order=True)


def test_diplomas_are_generated_even_if_not_exists_before(diploma_ru, diploma_en, student, mock_diploma_generator):
    diploma_en.delete()
    diploma_ru.delete()

    DiplomaRegenerator(student)()

    assert mock_diploma_generator.call_count == 2


def test_language_specific_diploma_not_regenerated_if_name_not_set(student, course, mock_diploma_generator):
    student.first_name_en = ''
    student.last_name_en = ''
    student.save()

    DiplomaRegenerator(student)()

    mock_diploma_generator.assert_called_once_with(course=course, student=student, language='RU')


def test_task(student, course, mock_diploma_generator, mocker):
    tasks.regenerate_diplomas.delay(student_id=student.id)

    mock_diploma_generator.assert_has_calls((
        mocker.call(course=course, student=student, language='RU'),
        mocker.call(course=course, student=student, language='EN'),
    ), any_order=True)


def test_sky_does_not_fall_if_there_is_no_template_for_generated_diploma(student, mock_send_mail, mock_diploma_generator):
    mock_diploma_generator.side_effect = DiplomaTemplate.DoesNotExist

    DiplomaRegenerator(student)()

    mock_send_mail.assert_not_called()


def test_email_is_sent(mock_send_mail, student):
    DiplomaRegenerator(student)()

    mock_send_mail.assert_called_once_with(
        to=student.email,
        template_id='diplomas_regenerated',
        disable_antispam=True,
    )


def test_no_diplomas_are_generated_when_student_didnt_set_name(another_user, mock_diploma_generator, mock_send_mail):
    DiplomaRegenerator(another_user)()

    mock_diploma_generator.assert_not_called()
    mock_send_mail.assert_not_called()
