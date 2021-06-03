import pytest

from triggers.base import BaseTrigger

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def user(mixer):
    return mixer.blend('users.User', first_name='Камаз', last_name='Отходов', email='kamaz.otkhodov@gmail.com')


@pytest.fixture
def course(mixer):
    return mixer.blend('products.Course', name='Курс кройки и шитья', full_name='Билет на курс кройки и шитья')


@pytest.fixture
def record(mixer, course):
    return mixer.blend('products.Record', course=course)


@pytest.fixture
def bundle(mixer):
    return mixer.blend('products.Bundle')


@pytest.fixture
def order(factory, user, course):
    return factory.order(user=user, giver=None, item=course)


@pytest.fixture
def test_trigger():
    class TestTrigger(BaseTrigger):
        name = 'test'

        def condition(self):
            return True

        def send(self):
            """mock it"""

    return TestTrigger
