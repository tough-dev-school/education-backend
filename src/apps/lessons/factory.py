from apps.lessons.models import Lesson
from apps.products.models import Course
from core.test.factory import FixtureFactory, register


@register
def lesson(self: FixtureFactory, course: Course | None = None, **kwargs: dict) -> Lesson:
    return self.mixer.blend(
        Lesson,
        course=course if course else self.course(),
        hidden=False,
        **kwargs,
    )
