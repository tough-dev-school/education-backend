import pytest

from triggers.base import BaseTrigger
from triggers import factory

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def user(mixer):
    return mixer.blend('users.User', first_name='Камаз', last_name='Отходов', email='kamaz.otkhodov@gmail.com')


@pytest.fixture
def course(mixer):
    return mixer.blend('courses.Course', name='Курс кройки и шитья', full_name='Билет на курс кройки и шитья')


@pytest.fixture
def record(mixer, course):
    return mixer.blend('courses.Record', course=course)


@pytest.fixture
def bundle(mixer):
    return mixer.blend('courses.Bundle')


@pytest.fixture
def order(mixer, user, course):
    order = mixer.blend('orders.Order', user=user)

    order.set_item(course)

    return order


@pytest.fixture
def test_trigger():

    @factory.register('test')
    class TestTrigger(BaseTrigger):

        @classmethod
        def run(cls):
            return True

        def condition(self):
            return True

        def send(self):
            """mock it"""

    return TestTrigger
