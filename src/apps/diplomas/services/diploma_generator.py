from dataclasses import dataclass
from urllib.parse import urljoin

import httpx
from django.conf import settings
from django.core.files.base import ContentFile
from retry import retry

from apps.diplomas.models import Diploma, DiplomaTemplate
from apps.products.models import Course
from apps.studying.models import Study
from apps.users.models import User
from core.services import BaseService
from core.types import Language


class WrongDiplomaServiceResponse(httpx.HTTPError):
    pass


@dataclass
class DiplomaGenerator(BaseService):
    course: Course
    student: User
    language: Language

    def act(self) -> Diploma:
        image = self.fetch_image()

        diploma = self.create_diploma()

        diploma.image.save(name="diploma.png", content=image)

        return diploma

    @property
    def study(self) -> Study:
        return Study.objects.get(student=self.student, course=self.course)

    @property
    def template(self) -> DiplomaTemplate:
        return DiplomaTemplate.objects.get(
            course=self.course,
            language=self.language,
            homework_accepted=self.study.homework_accepted,
        )

    def create_diploma(self) -> Diploma:
        return Diploma.objects.get_or_create(
            study=self.study,
            language=self.language,
        )[0]

    @retry((httpx.HTTPError, WrongDiplomaServiceResponse), tries=6, delay=1, backoff=2)
    def fetch_image(self) -> ContentFile:
        response = httpx.get(
            url=self.get_external_service_url(),
            params=self.get_template_context(),
            headers={
                "Authorization": f"Bearer {settings.DIPLOMA_GENERATOR_TOKEN}",
            },
        )

        if response.status_code != 200:
            raise WrongDiplomaServiceResponse(f"Got {response.status_code} status code: {response.text}")

        return ContentFile(response.content)

    def get_external_service_url(self) -> str:
        return urljoin(settings.DIPLOMA_GENERATOR_HOST, f"/{self.template.slug}.png")

    def get_template_context(self) -> dict:
        return {
            "name": self.student.get_printable_name(language=self.language),
            "sex": self.student.get_printable_gender()[:1],
            **self.course.diploma_template_context,
        }
