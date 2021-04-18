import pytest
from django.utils import timezone

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def course(mixer):
    return mixer.blend('products.Course')


@pytest.fixture
def question(mixer, course):
    question = mixer.blend('homework.Question')
    question.courses.add(course)

    return question


@pytest.fixture
def another_question(mixer, course):
    another_question = mixer.blend('homework.Question')
    another_question.courses.add(course)

    return another_question


@pytest.fixture
def answer(mixer, question, api):
    return mixer.blend('homework.Answer', question=question, author=api.user)


@pytest.fixture
def another_answer(mixer, question, api):
    return mixer.blend('homework.Answer', question=question, author=api.user)


@pytest.fixture
def purchase(mixer, course, api):
    return mixer.blend('orders.Order', user=api.user, course=course, paid=timezone.now())
