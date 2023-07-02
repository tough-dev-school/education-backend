import contextlib
from typing import Optional  # NOQA: I251
from urllib.parse import urljoin
import uuid

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db.models import QuerySet
from django.db.models import UniqueConstraint
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from app.models import models
from app.models import TimestampedModel
from notion.helpers import uuid_to_id
from users.models import User


class MaterialQuerySet(QuerySet):
    def active(self) -> QuerySet["Material"]:
        return self.filter(active=True)

    def for_student(self, student: User) -> QuerySet["Material"]:
        available_courses = apps.get_model("studying.Study").objects.filter(student=student).values("course")

        materials_from_available_courses = Material.objects.filter(active=True, course__in=available_courses)

        return Material.objects.filter(  # add materials with same page_ids but belonging to another courses
            page_id__in=materials_from_available_courses.values("page_id"),
        )

    def get_by_page_id_or_slug(self, page_id_or_slug: str) -> Optional["Material"]:
        with contextlib.suppress(ValidationError):
            return self.filter(
                Q(slug=page_id_or_slug) | Q(page_id=page_id_or_slug),
            ).first()


MaterialManager = models.Manager.from_queryset(MaterialQuerySet)


class Material(TimestampedModel):
    objects = MaterialManager()

    slug = models.UUIDField(default=uuid.uuid4, db_index=True, unique=True)

    title = models.CharField(_("Page title"), max_length=128, blank=True, help_text=_("Will be fetched automatically if empty"))
    course = models.ForeignKey("products.Course", on_delete=models.CASCADE)
    page_id = models.CharField(_("Notion page id"), max_length=64, db_index=True, help_text=_("Paste it from notion address bar"))
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


class MaterialFile(TimestampedModel):
    file = models.FileField(upload_to="materials", unique=True)  # NOQA: VNE002

    class Meta:
        verbose_name = _("Material file")
        verbose_name_plural = _("Material files")

    def __str__(self) -> str:
        return self.file.name

    def get_absolute_url(self) -> str:
        return self.file.url


class NotionCacheEntryQuerySet(QuerySet):
    def not_expired(self) -> "NotionCacheEntryQuerySet":
        time_now = timezone.now()
        return self.filter(expires__gt=time_now)


NotionCacheEntryManager = models.Manager.from_queryset(NotionCacheEntryQuerySet)


class NotionCacheEntry(TimestampedModel):
    objects = NotionCacheEntryManager()

    cache_key = models.CharField(max_length=255, unique=True, db_index=True)
    content = models.JSONField()
    expires = models.DateTimeField(db_index=True)

    def __str__(self) -> str:
        return self.cache_key
