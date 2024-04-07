from typing import Any

from axes.signals import user_locked_out
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import PermissionDenied


@receiver(user_locked_out)
def raise_permission_denied(*args: Any, **kwargs: Any) -> None:
    del args, kwargs

    raise PermissionDenied(_("Too many failed login attempts"))
