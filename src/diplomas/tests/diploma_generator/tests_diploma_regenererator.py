import pytest

from diplomas.services import DiplomaRegenerator

pytestmark = [pytest.mark.django_db]


@pytest.fixture
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


def test_diplomas_are_regenerated(student, course, diploma_generator, mocker):
    DiplomaRegenerator(student)()

    diploma_generator.asert_has_calls(mocker.call(course=course, student=student, language='ru'))
    diploma_generator.asert_has_calls(mocker.call(course=course, student=student, language='en'))


def test_no_diplomas_are_generated_when_there_are_no_diploams_for_user(another_user, diploma_generator):
    DiplomaRegenerator(another_user)()

    diploma_generator.assert_not_called()
