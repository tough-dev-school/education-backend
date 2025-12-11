import re
import uuid
from datetime import timedelta
from typing import cast
from urllib.parse import urljoin

from django.conf import settings
from django.contrib.auth.models import AbstractUser, Permission
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.core.exceptions import ValidationError
from django.db.models import Index, TextChoices
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from apps.diplomas.models import Languages
from core.files import RandomFileName
from core.models import TestUtilsMixin, models
from core.types import Language


def validate_hex_color(value: str | None) -> None:
    if value is None:
        return

    if not re.match(r"^#[0-9A-Fa-f]{6}$", value):
        raise ValidationError(
            _("Color should be a hex color, like '#bebebe'"),
            params={"value": value},
        )


class User(TestUtilsMixin, AbstractUser):
    class GENDERS(TextChoices):
        MALE = "male", _("Male")
        FEMALE = "female", _("Female")

    first_name_en = models.CharField(_("first name in english"), max_length=150, blank=True)
    last_name_en = models.CharField(_("last name in english"), max_length=150, blank=True)
    uuid = models.UUIDField(db_index=True, unique=True, default=uuid.uuid4)

    gender = models.CharField(_("Gender"), max_length=12, choices=GENDERS.choices, blank=True)

    random_name = models.CharField(_("Randomly generated name"), max_length=128, blank=True, null=True)

    linkedin_username = models.CharField(max_length=256, blank=True, db_index=True, default="")
    github_username = models.CharField(max_length=256, blank=True, db_index=True, default="")
    telegram_username = models.CharField(max_length=256, blank=True, db_index=True, default="")

    tags = ArrayField(models.CharField(max_length=512), default=list)
    avatar = models.ImageField(
        verbose_name=_("Avatar"),
        upload_to=RandomFileName("users/avatars"),
        null=True,
        blank=True,
    )

    rank = models.CharField(_("Rank"), max_length=32, blank=True, null=True)
    rank_label_color = models.CharField(_("Rank label color"), max_length=7, blank=True, null=True, validators=[validate_hex_color])

    class Meta:
        abstract = False
        indexes = [
            Index(fields=["date_joined"]),
            Index(fields=["email"]),
            GinIndex(fields=["tags"]),
        ]
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self) -> str:
        name = f"{self.first_name} {self.last_name}".strip()

        if len(name) < 3 and self.random_name is not None:
            name = self.random_name

        if len(name) < 3:
            return "Anonymous"

        return name

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
        language_values = [cast("Language", language) for language in Languages.values]
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
        This is a shortcut method for testing, never use it in production
        """
        path = perm.split(".")
        if len(path) == 3:  # exact path: app, model and codename
            [app_label, model, codename] = path

            permission = Permission.objects.get_by_natural_key(codename, app_label, model)
            if permission is None:
                raise Permission.DoesNotExist(f"Wrong permission path: '{perm}'")

            self.user_permissions.add(permission)

        if len(path) == 2:  # from app and codename, guessing the model
            [app_label, codename] = path

            opportunistic_permissions = Permission.objects.filter(content_type__app_label=app_label, codename=codename)

            if opportunistic_permissions.count() > 1:
                raise Permission.DoesNotExist(f"Found multiple permissions with app_label '{app_label}' and codename '{codename}'")

            if opportunistic_permissions.count() == 0:
                raise Permission.DoesNotExist(f"Wrong permission path, no permissions with app_label '{app_label}' and codename '{codename}'")

            self.user_permissions.add(opportunistic_permissions.get())


class AdminUserProxy(User):
    """Proxy model used for not-trusted administration of the user accounts"""

    class Meta:
        proxy = True
        verbose_name = _("Student")
        verbose_name_plural = _("Students")

    def __str__(self) -> str:
        return super().__str__()

    def get_absolute_url(self) -> str:
        from apps.a12n.utils import get_jwt
        from core.current_user import get_current_user

        current_user = get_current_user()
        if current_user is None:
            raise RuntimeError("This method should be called by an authenticated user")

        token = get_jwt(current_user, lifetime=timedelta(minutes=5))
        return urljoin(settings.FRONTEND_URL, f"/auth/as/{self.pk}/?t={token}")
