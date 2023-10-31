import pytest

from apps.diplomas.models import Diploma
from apps.diplomas.models import Languages

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def diploma(mixer, order):
    return mixer.blend("diplomas.Diploma", study=order.study, language=Languages.RU)


@pytest.fixture
def query():
    return lambda: Diploma.objects.filter_with_template()


def test_diploma_with_template_in_query(diploma, query):
    diplomas = query()

    assert diploma in diplomas


def test_exclude_diplomas_not_matching_template_course(factory, query, template, diploma):
    template.update(course=factory.course())

    diplomas = query()

    assert diploma not in diplomas


def test_exclude_diplomas_not_matching_template_language(query, template, diploma):
    template.update(language=Languages.EN)

    diplomas = query()

    assert diploma not in diplomas


def test_exclude_diplomas_not_matching_template_homework_accepted(query, template, diploma):
    template.update(homework_accepted=True)

    diplomas = query()

    assert diploma not in diplomas
