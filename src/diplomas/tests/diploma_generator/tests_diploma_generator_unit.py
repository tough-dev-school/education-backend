import pytest

from diplomas.models import DiplomaTemplate

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures('order', 'template'),
]


def test_study_object(generator, order):
    generator = generator(language='ru')

    assert generator.study == order.study, 'study object is returned'


@pytest.mark.parametrize(('gender', 'expected'), [
    ('', ''),
    ('female', 'f'),
    ('male', 'm'),
])
def test_sex(generator, gender, expected):
    generator = generator(language='ru')
    generator.student.gender = gender

    template_context = generator.get_template_context()

    assert template_context['sex'] == expected


def test_user_name_ru(generator):
    generator = generator(language='ru')
    generator.student.first_name = 'Авраам'
    generator.student.last_name = 'Линкольн'

    template_context = generator.get_template_context()

    assert template_context['name'] == 'Авраам Линкольн'


def test_user_name_en(generator):
    generator = generator(language='en')
    generator.student.first_name_en = 'Abraham'
    generator.student.last_name_en = 'Lincoln'

    template_context = generator.get_template_context()

    assert template_context['name'] == 'Abraham Lincoln'


def test_bad_language(generator):
    generator = generator(language='en')

    with pytest.raises(DiplomaTemplate.DoesNotExist):
        generator.get_external_service_url()


def test_no_template_for_homework(generator, order):
    order.study.homework_accepted = True
    order.study.save()

    generator = generator(language='ru')

    with pytest.raises(DiplomaTemplate.DoesNotExist):
        generator.get_external_service_url()


def test_external_service_url(generator, settings):
    settings.DIPLOMA_GENERATOR_HOST = 'https://secret.generator.com/'

    generator = generator(language='ru')

    assert generator.get_external_service_url() == 'https://secret.generator.com/test-template.png'
