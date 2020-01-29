import pytest

from triggers import factory

pytestmark = [pytest.mark.django_db]


def test_get_registered_trigger(test_trigger):
    assert factory.get('test') == test_trigger


def test_non_found():
    """Trigger without a registered in registry"""
    with pytest.raises(factory.TriggerNotRegistered):
        factory.get('supper dupper class')
