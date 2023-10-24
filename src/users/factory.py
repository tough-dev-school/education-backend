from typing import TYPE_CHECKING

from app.test.factory import register

if TYPE_CHECKING:
    from users.models import User


@register
def user(self, **kwargs: dict) -> "User":  # type: ignore[no-untyped-def]
    return self.mixer.blend("users.User", **kwargs)
