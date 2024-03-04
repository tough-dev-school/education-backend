from contextlib import nullcontext as does_not_raise

import pytest
from django.contrib.admin.models import CHANGE, LogEntry

from core.tasks import write_admin_log

pytestmark = [
    pytest.mark.auditlog,
    pytest.mark.django_db,
]


@pytest.fixture
def order(factory):
    return factory.order()


@pytest.mark.parametrize("model", ["order", "Order", "ORDER", "OrDeR"])
def test_model_param_is_case_insensitive(model, order, user):
    with does_not_raise():
        write_admin_log.delay(
            action_flag=CHANGE,
            app="orders",
            change_message="message",
            model=model,
            object_id=order.id,
            user_id=user.id,
        )

    assert LogEntry.objects.get()
