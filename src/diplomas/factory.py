from app.test.factory import register
from products.models import Course
from users.models import User


@register
def diploma(self, student: User = None, course: Course = None, **kwargs):
    if student is None:
        student = self.mixer.blend('users.User')

    if course is None:
        course = self.mixer.blend('products.Course')

    order = self.order(user=student, item=course)
    order.set_paid()
    order.refresh_from_db()

    return self.mixer.blend('diplomas.Diploma', study=order.study, **kwargs)
