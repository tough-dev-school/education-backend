from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from app.models import models


class User(AbstractUser):
    subscribed = models.BooleanField(_('Subscribed to newsletter'), default=False)

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

    def __str__(self):
        name = self.first_name + ' ' + self.last_name

        if len(name) < 3:
            return self.username

        return name.strip()
