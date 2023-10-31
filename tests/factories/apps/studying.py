from typing import TYPE_CHECKING

from core.test.factory import register

if TYPE_CHECKING:
    from apps.studying.models import Study


@register
def study(self, **kwargs: dict) -> "Study":  # type: ignore[no-untyped-def]
    return self.mixer.blend("studying.Study", **kwargs)
