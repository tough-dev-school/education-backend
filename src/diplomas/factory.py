from typing import Optional

from app.test.factory import register
from products.models import Course
from users.models import User


@register
def diploma(self, student: Optional[User] = None, course: Optional[Course] = None, **kwargs):
    order = self.order(
        user=student or self.mixer.blend('users.User'),
        item=course or self.mixer.blend('products.Course'),
    )
    order.set_paid()
    order.refresh_from_db()

    return self.mixer.blend('diplomas.Diploma', study=order.study, **kwargs)
