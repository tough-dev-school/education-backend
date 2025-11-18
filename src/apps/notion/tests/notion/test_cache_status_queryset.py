from datetime import datetime, timezone

import pytest
from django.db.models import QuerySet

from apps.notion.models import Material, NotionCacheEntryStatus

pytestmark = [pytest.mark.django_db]


def queryset() -> QuerySet[Material]:
    return Material.objects.with_cache_status()


def test_materials_without_cache_status_are_still_available(material):
    assert material in list(queryset())


def test_started(material):
    NotionCacheEntryStatus.objects.create(
        page_id=material.page_id,
        fetch_started="2032-12-01 15:30:00+03:00",
        fetch_complete=None,
    )

    material = queryset()[0]

    assert material.fetch_started == datetime(2032, 12, 1, 12, 30, tzinfo=timezone.utc)
    assert material.fetch_complete is None


def test_complete(material):
    NotionCacheEntryStatus.objects.create(
        page_id=material.page_id,
        fetch_started="2032-12-01 15:30:00+03:00",
        fetch_complete="2032-12-01 15:40:00+03:00",
    )

    material = queryset()[0]

    assert material.fetch_complete == datetime(2032, 12, 1, 12, 40, tzinfo=timezone.utc)
