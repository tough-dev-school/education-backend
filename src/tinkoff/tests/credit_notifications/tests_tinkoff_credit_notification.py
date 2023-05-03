from decimal import Decimal
import pytest

from tinkoff.models import CreditNotification

pytestmark = [pytest.mark.django_db]


def test(api, notification, order):
    api.post("/api/v2/banking/tinkoff-credit-notifications/", notification, expected_status_code=200)

    created = CreditNotification.objects.last()

    assert created.order == order
    assert created.status == "approved"
    assert created.first_payment == 0
    assert created.order_amount == 5200
    assert created.credit_amount == 5200
    assert created.product == "credit"
    assert created.term == 6
    assert created.monthly_payment == Decimal("944.32")
    assert created.first_name == "Удой"
    assert created.last_name == "Коровов"
    assert created.middle_name is None
    assert created.phone == "+79031234567"
    assert created.loan_number is None
    assert created.email == "konstantin13@ip.biz"


@pytest.mark.parametrize(
    "field",
    [
        "first_name",
        "last_name",
        "loan_number",
        "email",
        "phone",
    ],
)
def test_null_fields(api, notification, field):
    notification[field] = None

    api.post("/api/v2/banking/tinkoff-credit-notifications/", notification, expected_status_code=200)

    assert CreditNotification.objects.exists()


@pytest.mark.parametrize(
    "field",
    [
        "first_name",
        "last_name",
        "loan_number",
        "email",
        "phone",
    ],
)
def test_empty_fields(api, notification, field):
    notification[field] = ""

    api.post("/api/v2/banking/tinkoff-credit-notifications/", notification, expected_status_code=200)

    assert CreditNotification.objects.exists()
