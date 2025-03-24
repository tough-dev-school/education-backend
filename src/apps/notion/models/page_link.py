from typing import TYPE_CHECKING

from django.db import transaction
from django.db.models import Index, UniqueConstraint
from django.utils.translation import gettext_lazy as _

from core.models import TimestampedModel, models

if TYPE_CHECKING:
    from apps.notion.types import NotionId


class PageLink(TimestampedModel):
    source = models.CharField(_("Source page notion id"), max_length=64, db_index=True)
    destination = models.CharField(_("Destination page notion id"), max_length=64, db_index=True)

    class Meta:
        indexes = [
            Index(fields=["source", "destination"]),
        ]
        constraints = [
            UniqueConstraint(fields=["source", "destination"], name="unique_link_pair"),
        ]

    @classmethod
    def update_page_links(cls, page: "NotionId", links: list["NotionId"]) -> None:
        with transaction.atomic():
            cls.objects.filter(source=page).all().delete()
            cls.objects.bulk_create([cls(source=page, destination=link) for link in set(links)])
