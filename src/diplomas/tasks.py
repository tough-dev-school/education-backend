from requests.exceptions import RequestException

from app.celery import celery
from diplomas.services import DiplomaGenerator
from products.models import Course
from users.models import User


@celery.task(
    acks_late=True,
    rate_limit='1/s',
    autoretry_for=[RequestException],
    retry_kwargs={
        'max_retries': 20,
        'countdown': 3,
    },
)
def generate_diploma(student_id: int, course_id: int, language: str, with_homework: bool):
    generator = DiplomaGenerator(
        student=User.objects.get(pk=student_id),
        course=Course.objects.get(pk=course_id),
        language=language,
        with_homework=with_homework,
    )

    generator()
