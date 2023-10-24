from typing import TYPE_CHECKING

from app.test.factory import register

if TYPE_CHECKING:
    from studying.models import Study


@register
def study(self, **kwargs: dict) -> "Study":  # type: ignore[no-untyped-def]
    return self.mixer.blend("studying.Study", **kwargs)
