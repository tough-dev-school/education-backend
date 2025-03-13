import pytest
from django.contrib.admin.models import CHANGE, LogEntry
from django.contrib.contenttypes.models import ContentType

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time("2032-12-24 15:38"),
]


@pytest.mark.auditlog
@pytest.mark.usefixtures("_set_current_user")
def test_auditlog(completer, deal, user):
    completer(deal=deal)()

    log = LogEntry.objects.filter(
        content_type=ContentType.objects.get_for_model(deal).id,
    ).last()
    assert log.action_flag == CHANGE
    assert log.change_message == "Deal completed"
    assert log.user == user
    assert log.object_id == str(deal.id)
    assert log.object_repr == str(deal)
