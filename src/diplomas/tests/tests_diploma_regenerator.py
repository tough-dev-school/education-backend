import pytest

from diplomas import tasks
from diplomas.services import DiplomaRegenerator

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def diploma_generator(mocker):
    return mocker.patch('diplomas.services.diploma_generator.DiplomaGenerator.__init__', return_value=None)


@pytest.fixture(autouse=True)
def _disable_actual_generator_call(mocker):
    mocker.patch('diplomas.services.diploma_generator.DiplomaGenerator.__call__')


@pytest.fixture(autouse=True)
def diploma_ru(mixer, order):
    return mixer.blend('diplomas.Diploma', study=order.study, language='ru')


@pytest.fixture(autouse=True)
def diploma_en(mixer, order):
    return mixer.blend('diplomas.Diploma', study=order.study, language='en')


@pytest.fixture
def send_mail(mocker):
    return mocker.patch('app.tasks.mail.TemplOwl.send')


def test_diplomas_are_regenerated(student, course, diploma_generator, mocker):
    DiplomaRegenerator(student)()

    diploma_generator.asert_has_calls(mocker.call(course=course, student=student, language='ru'))
    diploma_generator.asert_has_calls(mocker.call(course=course, student=student, language='en'))


def test_task(student, course, diploma_generator, mocker):
    tasks.regenerate_diplomas.delay(student_id=student.id)

    diploma_generator.asert_has_calls(mocker.call(course=course, student=student, language='ru'))
    diploma_generator.asert_has_calls(mocker.call(course=course, student=student, language='en'))


def test_emai_is_sent(send_mail, student):
    DiplomaRegenerator(student)()

    send_mail.assert_called_once()


def test_no_diplomas_are_generated_when_there_are_no_diploams_for_user(another_user, diploma_generator, send_mail):
    DiplomaRegenerator(another_user)()

    diploma_generator.assert_not_called()

    send_mail.assert_not_called()
