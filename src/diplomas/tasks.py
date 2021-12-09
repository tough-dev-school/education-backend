from requests.exceptions import RequestException

from app.celery import celery
from app.types import Language
from diplomas.services import DiplomaGenerator
from products.models import Course
from users.models import User


@celery.task(
    acks_late=True,
    rate_limit='3/s',
    autoretry_for=[RequestException],
    max_retries=40,
)
def generate_diploma(student_id: int, course_id: int, language: Language):
    generator = DiplomaGenerator(
        student=User.objects.get(pk=student_id),
        course=Course.objects.get(pk=course_id),
        language=language,
    )

    generator()
