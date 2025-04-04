from apps.lms.models import Lesson, Module
from apps.products.models import Course
from core.test.factory import FixtureFactory, register


@register
def lesson(self: FixtureFactory, module: Module | None = None, **kwargs: dict) -> Lesson:
    return self.mixer.blend(
        Lesson,
        module=module if module else self.module(),
        hidden=False,
        **kwargs,
    )


@register
def module(self: FixtureFactory, course: Course | None = None, **kwargs: dict) -> Module:
    return self.mixer.blend(
        Module,
        course=course if course else self.course(),
        hidden=False,
        **kwargs,
    )
