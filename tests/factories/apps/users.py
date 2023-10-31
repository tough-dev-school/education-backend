from typing import TYPE_CHECKING

from core.test.factory import register

if TYPE_CHECKING:
    from apps.users.models import User


@register
def user(self, **kwargs: dict) -> "User":  # type: ignore[no-untyped-def]
    return self.mixer.blend("users.User", **kwargs)
