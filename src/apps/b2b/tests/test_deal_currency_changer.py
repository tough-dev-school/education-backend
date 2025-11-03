from decimal import Decimal

import pytest
from django.contrib.admin.models import CHANGE, LogEntry
from django.contrib.contenttypes.models import ContentType

from apps.b2b.services import DealCurrencyChanger

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("_set_current_user", "usd"),
]


@pytest.mark.parametrize("new_currency_code", ["usd", "UsD"])
def test(deal, new_currency_code):
    assert deal.currency == "RUB"

    DealCurrencyChanger(deal=deal, new_currency_code=new_currency_code)()
    deal.refresh_from_db()

    assert deal.currency == "USD"
    assert deal.currency_rate_on_creation == Decimal(100)


def test_wrong_currency_code(deal):
    with pytest.raises(TypeError):
        DealCurrencyChanger(deal=deal, new_currency_code="NONEXISTANT-STUPID-CODE")()


@pytest.mark.auditlog
def test_auditlog(deal, user):
    DealCurrencyChanger(deal=deal, new_currency_code="usd")()

    log = LogEntry.objects.filter(
        content_type=ContentType.objects.get_for_model(deal).id,
    ).last()

    assert log.action_flag == CHANGE
    assert "currency" in log.change_message
    assert "USD" in log.change_message

    assert log.user == user
    assert log.object_id == str(deal.id)
    assert log.object_repr == str(deal)
