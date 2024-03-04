from typing import Any

from apps.diplomas.models import Diploma
from apps.products.models import Course
from apps.users.models import User
from core.test.factory import register


@register
def diploma(self: Any, student: User | None = None, course: Course | None = None, **kwargs: dict[str, Any]) -> Diploma:
    order = self.order(
        user=student or self.mixer.blend("users.User"),
        item=course or self.course(),
    )
    order.set_paid()
    order.refresh_from_db()

    return self.mixer.blend("diplomas.Diploma", study=order.study, **kwargs)
