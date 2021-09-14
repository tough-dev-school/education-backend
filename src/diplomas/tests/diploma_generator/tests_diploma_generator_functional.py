import pytest

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def _set_diploma_generator_url(settings):
    settings.DIPLOMA_GENERATOR_HOST = 'https://secret.generator.com/'
    settings.DIPLOMA_GENERATOR_TOKEN = 'zeroc00l'


@pytest.mark.usefixtures('template')
def test_downloading_image(generator, student, course):
    generator = generator(language='ru', with_homework=True)
    generator.http_mock.get('https://secret.generator.com/test-template.png?name=%D0%9E%D0%B2%D0%B8%D1%80+%D0%9A%D1%80%D0%B8%D0%B2%D0%BE%D0%BC%D0%B0%D0%B7%D0%BE%D0%B2&sex=m', content=b'TYPICAL MAC USER JPG')

    diploma = generator()

    assert diploma.image.read() == b'TYPICAL MAC USER JPG'
    assert diploma.study.student == student
    assert diploma.study.course == course
