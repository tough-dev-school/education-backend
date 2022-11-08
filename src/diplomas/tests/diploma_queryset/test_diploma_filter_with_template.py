import pytest

from diplomas.models import Diploma, Languages

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def diploma(mixer, order):
    return mixer.blend('diplomas.Diploma', study=order.study, language=Languages.RU)


@pytest.fixture
def query():
    return lambda: Diploma.objects.filter_with_template()


def test_diploma_with_template_in_query(diploma, query):
    diplomas = query()

    assert diploma in diplomas


def test_exclude_diplomas_not_matching_template_course(mixer, query, template, diploma):
    template.setattr_and_save('course', mixer.blend('products.Course'))

    diplomas = query()

    assert diploma not in diplomas


def test_exclude_diplomas_not_matching_template_language(query, template, diploma):
    template.setattr_and_save('language', Languages.EN)

    diplomas = query()

    assert diploma not in diplomas


def test_exclude_diplomas_not_matching_template_homework_accepted(query, template, diploma):
    template.setattr_and_save('homework_accepted', True)

    diplomas = query()

    assert diploma not in diplomas
