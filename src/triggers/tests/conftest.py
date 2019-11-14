import pytest

from triggers.base import BaseTrigger

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def order(mixer):
    return mixer.blend('orders.Order')


@pytest.fixture
def test_trigger():
    class TestTrigger(BaseTrigger):
        name = 'test'

        def condition(self):
            return True

        def send(self):
            """mock it"""

    return TestTrigger
