import pytest

from triggers import factory

pytestmark = [pytest.mark.django_db]

@pytest.fixture
def call_record_feedback_trigger(mocker):
    return mocker.patch('triggers.record_feedback.RecordFeedbackTrigger.__call__')

def test_factory_run(call_record_feedback_trigger, order):
    factory.run('record_feedback', order)

    call_record_feedback_trigger.assert_called_once()






