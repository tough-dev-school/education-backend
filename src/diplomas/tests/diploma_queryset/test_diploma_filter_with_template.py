import pytest

from diplomas.models import Diploma

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def diploma(mixer, order):
    return mixer.blend('diplomas.Diploma', study=order.study, language='RU')


@pytest.fixture
def query():
    return lambda: Diploma.objects.filter_with_template()


def test_diploma_with_template_in_query(diploma, query):
    diplomas = query()

    assert diploma in diplomas


def test_exclude_diplomas_not_matching_template_course(mixer, query, template):
    template.setattr_and_save('course', mixer.blend('products.Course'))

    diplomas = query()

    assert diplomas.count() == 0


def test_exclude_diplomas_not_matching_template_language(query, template):
    template.setattr_and_save('language', 'EN')

    diplomas = query()

    assert diplomas.count() == 0


def test_exclude_diplomas_not_matching_template_homework_accepted(query, template):
    template.setattr_and_save('homework_accepted', True)

    diplomas = query()

    assert diplomas.count() == 0
