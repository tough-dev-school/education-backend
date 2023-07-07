from typing import Any

from app.test.factory import register
from diplomas.models import Diploma
from products.models import Course
from users.models import User


@register
def diploma(self: Any, student: User | None = None, course: Course | None = None, **kwargs: dict[str, Any]) -> Diploma:
    order = self.order(
        user=student or self.mixer.blend("users.User"),
        item=course or self.course(),
    )
    order.set_paid()
    order.refresh_from_db()

    return self.mixer.blend("diplomas.Diploma", study=order.study, **kwargs)
