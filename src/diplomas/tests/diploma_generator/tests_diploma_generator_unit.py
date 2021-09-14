import pytest

pytestmark = [pytest.mark.django_db]


def test_study_object(generator, order):
    generator = generator(language='ru', with_homework=False)

    assert generator.study == order.study, 'study object is returned'


@pytest.mark.parametrize(('gender', 'expected'), [
    ('', ''),
    ('female', 'f'),
    ('male', 'm'),
])
def test_sex(generator, gender, expected):
    generator = generator(language='ru', with_homework=False)
    generator.student.gender = gender

    template_context = generator.get_template_context()

    assert template_context['sex'] == expected


def test_user_name(generator):
    generator = generator(language='ru', with_homework=False)
    generator.student.first_name = 'Авраам'
    generator.student.last_name = 'Линкольн'

    template_context = generator.get_template_context()

    assert template_context['name'] == 'Авраам Линкольн'


@pytest.mark.usefixtures('template')
def test_external_service_url(generator, settings):
    settings.DIPLOMA_GENERATOR_HOST = 'https://secret.generator.com/'

    generator = generator(language='ru', with_homework=True)

    assert generator.get_external_service_url() == 'https://secret.generator.com/test-template.png'
