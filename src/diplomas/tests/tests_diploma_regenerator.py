import pytest

from diplomas import tasks
from diplomas.models import DiplomaTemplate
from diplomas.services import DiplomaRegenerator

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.skip(reason='fixme'),
]


@pytest.fixture(autouse=True)
def diploma_generator(mocker):
    return mocker.patch('diplomas.services.diploma_regenerator.DiplomaGenerator.__init__', return_value=None)


@pytest.fixture(autouse=True)
def run_diploma_generation(mocker):
    return mocker.patch('diplomas.services.diploma_generator.DiplomaGenerator.__call__')


@pytest.fixture(autouse=True)
def diploma_ru(mixer, order):
    return mixer.blend('diplomas.Diploma', study=order.study, language='ru')


@pytest.fixture(autouse=True)
def diploma_en(mixer, order):
    return mixer.blend('diplomas.Diploma', study=order.study, language='en')


@pytest.fixture
def send_mail(mocker):
    return mocker.patch('app.tasks.mail.TemplOwl.send')


def test_diplomas_are_regenerated(student, course, diploma_generator, mocker, order):
    DiplomaRegenerator(student)()

    diploma_generator.assert_has_calls(mocker.call(course=course, student=student, language='ru'))
    diploma_generator.assert_has_calls(mocker.call(course=course, student=student, language='en'))


def test_task(student, course, diploma_generator, mocker, order):
    tasks.regenerate_diplomas.delay(student_id=student.id)

    diploma_generator.assert_has_calls(mocker.call(course=course, student=student, language='ru'))
    diploma_generator.assert_has_calls(mocker.call(course=course, student=student, language='en'))


def test_sky_does_not_fall_if_there_is_no_template_for_generated_diploma(student, run_diploma_generation, send_mail):
    run_diploma_generation.side_effect = DiplomaTemplate.DoesNotExist

    DiplomaRegenerator(student)()

    send_mail.assert_not_called()


def test_emai_is_sent(send_mail, student):
    DiplomaRegenerator(student)()

    send_mail.assert_called_once()


def test_no_diplomas_are_generated_when_there_are_no_diploams_for_user(another_user, diploma_generator, send_mail):
    DiplomaRegenerator(another_user)()

    diploma_generator.assert_not_called()

    send_mail.assert_not_called()
