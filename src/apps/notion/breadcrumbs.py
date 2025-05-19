from apps.lms.models import Lesson
from apps.notion.models import Material


def get_lesson(material: Material) -> Lesson | None:
    """Find a lesson to which the material is attached.

    We need this method becuase materials still have ForeignKey to courses use it for access checks
    """

    return Lesson.objects.filter(module__course_id=material.course_id, material_id=material.id).first()
