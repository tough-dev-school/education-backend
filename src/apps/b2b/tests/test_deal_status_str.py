import pytest
from django.utils import timezone

from apps.b2b.services import DealCompleter

pytestmark = [pytest.mark.django_db]


def test_in_progress_by_default(deal):
    assert deal.get_status_representation() == "In progress"


def test_complete(deal):
    DealCompleter(deal=deal)()

    assert deal.get_status_representation() == "Complete"


def test_shipped_only(deal):
    DealCompleter(deal=deal, ship_only=True)()

    assert deal.get_status_representation() == "Shipped without payment"


def test_complete_after_shipped_only(deal):
    DealCompleter(deal=deal, ship_only=True)()
    DealCompleter(deal=deal)()

    assert deal.get_status_representation() == "Complete"


def test_canceled(deal):
    deal.canceled = timezone.now()

    assert deal.get_status_representation() == "Canceled"
