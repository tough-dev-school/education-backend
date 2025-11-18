# ruff: noqa: S608, S611
import contextlib
import uuid
from typing import Optional
from urllib.parse import urljoin

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q, QuerySet, UniqueConstraint
from django.db.models.expressions import RawSQL
from django.utils.translation import gettext_lazy as _

from apps.notion.id import uuid_to_id
from apps.users.models import User
from core.models import TimestampedModel, models


class MaterialQuerySet(QuerySet):
    def active(self) -> QuerySet["Material"]:
        return self.filter(active=True)

    def for_student(self, student: User) -> QuerySet["Material"]:
        available_course_ids = list(apps.get_model("studying.Study").objects.filter(student=student).values_list("course", flat=True))

        if len(available_course_ids) == 0:
            return Material.objects.none()

        # Didn't want to use django-tree-queries as we do in the homework app, cuz after time
        # i see no value in it over raw SQL

        return Material.objects.filter(  # this query cost me $1.56
            page_id__in=RawSQL(
                f"""
                WITH RECURSIVE accessible_pages AS (
                    -- Base case: directly accessible page IDs from available courses
                    SELECT page_id FROM {Material._meta.db_table}
                    WHERE active = TRUE AND course_id = ANY(%s)

                    UNION

                    -- Recursive case: child pages linked from any accessible page
                    SELECT pl.destination
                    FROM {apps.get_model("notion.PageLink")._meta.db_table} pl
                    JOIN accessible_pages ap ON pl.source = ap.page_id
                )
                SELECT page_id FROM accessible_pages
            """,
                [available_course_ids],
            )
        )

    def get_by_page_id_or_slug(self, page_id_or_slug: str) -> Optional["Material"]:
        with contextlib.suppress(ValidationError):
            return self.filter(
                Q(slug=page_id_or_slug) | Q(page_id=page_id_or_slug),
            ).first()

    def with_cache_status(self) -> "MaterialQuerySet":
        """Annotating cache status via RawSQL cuz we have no conventional ForeignKey between material and its cache (for no reason)"""
        NotionCacheEntryStatus = apps.get_model("notion.NotionCacheEntryStatus")

        return self.annotate(
            fetch_started=RawSQL(
                f"""
                SELECT fetch_started
                FROM {NotionCacheEntryStatus._meta.db_table}
                WHERE {NotionCacheEntryStatus._meta.db_table}.page_id = {Material._meta.db_table}.page_id
                """,
                [],
            ),
            fetch_complete=RawSQL(
                f"""
                SELECT fetch_complete
                FROM {NotionCacheEntryStatus._meta.db_table}
                WHERE {NotionCacheEntryStatus._meta.db_table}.page_id = {Material._meta.db_table}.page_id
                """,
                [],
            ),
        )


MaterialManager = models.Manager.from_queryset(MaterialQuerySet)


class Material(TimestampedModel):
    objects = MaterialManager()

    slug = models.UUIDField(_("Our page id"), default=uuid.uuid4, db_index=True, unique=True)

    title = models.CharField(_("Page title"), max_length=128, blank=True, help_text=_("Will be fetched automatically if empty"))
    course = models.ForeignKey("products.Course", on_delete=models.CASCADE)
    page_id = models.CharField(_("Notion page id"), max_length=64, db_index=True, help_text=_("Paste it from apps.notion address bar"))
    active = models.BooleanField(_("Active"), default=True)
    is_home_page = models.BooleanField(_("Is home page of the course"), default=False)

    class Meta:
        verbose_name = _("Notion material")
        verbose_name_plural = _("Notion materials")
        constraints = [
            UniqueConstraint(fields=["course", "page_id"], name="single_page_per_single_course"),
        ]
        permissions = [
            ("see_all_materials", _("May access materials from every course")),
        ]

    def __str__(self) -> str:
        return f"{self.course} - {self.title}"

    def get_absolute_url(self) -> str:
        slug = uuid_to_id(str(self.slug))
        return urljoin(settings.FRONTEND_URL, f"materials/{slug}/")

    def get_notion_url(self) -> str:
        return f"https://notion.so/1-{self.page_id}"

    def get_short_slug(self) -> str:
        return uuid_to_id(str(self.slug))
