import pytest

from triggers import factory

pytestmark = [pytest.mark.django_db]


def test_class_register():
    @factory.register('test')
    class TestClass():
        some_value = 'ololo'

        def __init__(self):
            print('Kill all humans')

    assert factory._registry['test1'] == TestClass


