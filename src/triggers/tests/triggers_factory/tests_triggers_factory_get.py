import pytest

from triggers import factory
from triggers.record_feedback import RecordFeedbackTrigger

pytestmark = [pytest.mark.django_db]

def test_record_feedback_trigger():
    assert factory.get(RecordFeedbackTrigger.name) == RecordFeedbackTrigger


def test_non_found():
    """Trigger without a registered in registry"""
    with pytest.raises(factory.TriggerNotRegistered):
        factory.get('supper dupper class')

