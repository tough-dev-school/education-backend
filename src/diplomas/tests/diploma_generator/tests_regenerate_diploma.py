import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def generate_diploma(mocker):
    return mocker.patch('diplomas.models.DiplomaTemplate.generate_diploma')


@pytest.fixture
def diploma(factory, student, course):
    return factory.diploma(student=student, course=course)


@pytest.fixture
def english_template(mixer, course):
    return mixer.blend('diplomas.DiplomaTemplate', slug='test-template-en', course=course, language='en')


@pytest.mark.usefixtures('template')
def test_regenrate_diploma_calls_diploma_generation(diploma, generate_diploma, student):
    diploma.regenerate()

    generate_diploma.assert_called_once_with(student=student)


@pytest.mark.usefixtures('template', 'english_template')
def test_regenrate_diploma_calls_diploma_generation_per_each_template(diploma, generate_diploma, student, mocker):
    diploma.regenerate()

    generate_diploma.assert_has_calls([
        mocker.call(student=student),
        mocker.call(student=student),
    ])


@pytest.mark.usefixtures('template', 'english_template')
def test_regenerate_diploma_returns_count(diploma):
    assert diploma.regenerate() == 2
