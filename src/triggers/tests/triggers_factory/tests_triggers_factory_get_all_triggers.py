import pytest

from triggers import factory
from triggers.record_feedback import RecordFeedbackTrigger

pytestmark = [pytest.mark.django_db]


def test_specific_trigger_in_get_all_triggers():

    assert RecordFeedbackTrigger in factory.get_all_triggers()


def test_count_triggers_in_get_all_triggers():
    REGISTERED_TRIGGERS_COUNT = 1

    assert len(factory.get_all_triggers()) == REGISTERED_TRIGGERS_COUNT
