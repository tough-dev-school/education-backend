import httpx

from app.celery import celery
from app.types import Language
from diplomas.services import DiplomaGenerator
from diplomas.services import DiplomaRegenerator
from diplomas.services.diploma_generator import WrongDiplomaServiceResponse
from products.models import Course
from users.models import User


@celery.task(
    acks_late=True,
    rate_limit="1/s",
    autoretry_for=[WrongDiplomaServiceResponse, httpx.RequestError],
    max_retries=10,
    soft_time_limit=240,
)
def generate_diploma(student_id: int, course_id: int, language: Language) -> None:
    generator = DiplomaGenerator(
        student=User.objects.get(pk=student_id),
        course=Course.objects.get(pk=course_id),
        language=language,
    )

    generator()


@celery.task(
    acks_late=True,
    rate_limit="3/s",
    autoretry_for=[WrongDiplomaServiceResponse],
    max_retries=10,
)
def regenerate_diplomas(student_id: int) -> None:
    DiplomaRegenerator(
        student=User.objects.get(pk=student_id),
    )()
