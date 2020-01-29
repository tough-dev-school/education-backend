import pytest

from triggers import factory

pytestmark = [pytest.mark.django_db]


def test_specific_trigger_in_get_all_triggers(test_trigger):

    assert test_trigger in factory.get_all_triggers()


def test_count_triggers_in_get_all_triggers():

    assert len(factory.get_all_triggers()) == 1
