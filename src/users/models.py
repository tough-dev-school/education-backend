from typing import cast
from urllib.parse import urljoin
import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Permission
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.db.models import TextChoices
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from app.models import models
from app.types import Language
from diplomas.models import Languages


class User(AbstractUser):
    class GENDERS(TextChoices):
        MALE = "male", _("Male")
        FEMALE = "female", _("Female")

    subscribed = models.BooleanField(_("Subscribed to newsletter"), default=False)
    first_name_en = models.CharField(_("first name in english"), max_length=150, blank=True)
    last_name_en = models.CharField(_("last name in english"), max_length=150, blank=True)
    uuid = models.UUIDField(db_index=True, unique=True, default=uuid.uuid4)

    gender = models.CharField(_("Gender"), max_length=12, choices=GENDERS.choices, blank=True)

    linkedin_username = models.CharField(max_length=256, blank=True, db_index=True, default="")
    github_username = models.CharField(max_length=256, blank=True, db_index=True, default="")
    telegram_username = models.CharField(max_length=256, blank=True, db_index=True, default="")

    tags = ArrayField(models.CharField(max_length=512), default=list)

    class Meta(AbstractUser.Meta):
        abstract = False  # type: ignore[assignment]
        indexes = [GinIndex(fields=["tags"])]
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self) -> str:
        name = f"{self.first_name} {self.last_name}"

        if len(name) < 3:
            return "Anonymous"

        return name.strip()

    @classmethod
    def parse_name(cls, name: str) -> dict:
        parts = name.split(" ", 2)

        if len(parts) == 1:
            return {"first_name": parts[0]}

        if len(parts) == 2:
            return {"first_name": parts[0], "last_name": parts[1]}

        return {"first_name": parts[0], "last_name": " ".join(parts[1:])}

    @cached_property
    def diploma_languages(self) -> set[Language]:
        language_values = [cast(Language, language) for language in Languages.values]
        return {language for language in language_values if self.get_printable_name(language) is not None}

    def get_printable_name(self, language: Language) -> str | None:
        if language.lower() == "ru":
            name = f"{self.first_name} {self.last_name}"
        else:
            name = f"{self.first_name_en} {self.last_name_en}"

        name = name.strip()

        if len(name) > 3:
            return name

    def get_printable_gender(self) -> str:
        if self.gender and len(self.gender):
            return self.gender

        return "male"  # sorry, flex scope

    def add_perm(self, perm: str) -> None:
        """Add permission to the user.
        This is a shortcut method for testing, please do not use in production
        """
        [app_label, model, codename] = perm.split(".")

        permission = Permission.objects.get_by_natural_key(codename, app_label, model)
        if permission is not None:
            self.user_permissions.add(permission)


class Student(User):
    """Proxy model used for not-trusted administration of the user accounts"""

    class Meta:
        proxy = True
        verbose_name = _("Student")
        verbose_name_plural = _("Students")

    def __str__(self) -> str:
        return super().__str__()

    def get_absolute_url(self) -> str:
        return urljoin(settings.FRONTEND_URL, f"/auth/as/{self.pk}/")
