from typing import Literal, Optional, Union

import uuid
from django.contrib.auth.models import AbstractUser, Permission
from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _

from app.models import models


class User(AbstractUser):
    class GENDERS(TextChoices):
        MALE = 'male', _('Male')
        FEMALE = 'female', _('Female')

    subscribed = models.BooleanField(_('Subscribed to newsletter'), default=False)
    first_name_en = models.CharField(_('first name in english'), max_length=150, blank=True)
    last_name_en = models.CharField(_('last name in english'), max_length=150, blank=True)
    uuid = models.UUIDField(db_index=True, unique=True, default=uuid.uuid4)

    gender = models.CharField(_('Gender'), max_length=12, choices=GENDERS.choices, blank=True)

    @classmethod
    def parse_name(cls, name: str) -> dict:
        if name is None:
            return {}

        parts = name.split(' ', 2)

        if len(parts) == 1:
            return {'first_name': parts[0]}

        if len(parts) == 2:
            return {'first_name': parts[0], 'last_name': parts[1]}

        return {'first_name': parts[0], 'last_name': ' '.join(parts[1:])}

    def __str__(self) -> str:
        name = f'{self.first_name} {self.last_name}'

        if len(name) < 3:
            return 'Anonymous'

        return name.strip()

    def get_printable_name(self, language: Union[Literal['ru'], Literal['en']]) -> Optional[str]:
        if language == 'ru':
            name = f'{self.first_name} {self.last_name}'
        else:
            name = f'{self.first_name_en} {self.last_name_en}'

        name = name.strip()

        if len(name) > 3:
            return name

    def add_perm(self, perm):
        """Add permission to the user.
        This is a shortcut method for testing, please do not use in production
        """
        [app_label, model, codename] = perm.split('.')

        permission = Permission.objects.get_by_natural_key(codename, app_label, model)
        if permission is not None:
            self.user_permissions.add(permission)


class Student(User):
    """Proxy model used for not-trusted administration of the user accounts
    """
    class Meta:
        proxy = True
        verbose_name = _('Student')
        verbose_name_plural = _('Students')
