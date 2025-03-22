import pytest

from apps.notion.models import PageLink

pytestmark = pytest.mark.django_db


def test_old_links_are_deleted():
    PageLink.objects.create(source="id-1", destination="id-2")

    PageLink.update_page_links(page="id-1", links=["id-3", "id-4"])

    assert not PageLink.objects.filter(destination="id-2").exists()


def test_links_are_created():
    PageLink.update_page_links(page="id-1", links=["id-2", "id-3"])

    assert PageLink.objects.count() == 2


def test_duplicate_links_are_ignored():
    PageLink.update_page_links(page="id-1", links=["id-2", "id-2", "id-3"])

    links = list(PageLink.objects.all().order_by("destination").values_list("destination", flat=True))

    assert links == ["id-2", "id-3"]
