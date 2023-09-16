from mailing.tasks import send_mail
from products.models import Course
from studying import shipment_factory as factory
from studying.models import Study
from studying.shipment.base import BaseShipment


@factory.register(Course)
class CourseShipment(BaseShipment):
    @property
    def course(self) -> Course:
        return self.stuff_to_ship

    def ship(self) -> None:
        self.create_study_model()

        self.send_welcome_letter()

    def unship(self) -> None:
        self.remove_study_model()

    def create_study_model(self) -> None:
        Study.objects.get_or_create(
            course=self.course,
            student=self.user,
            defaults=dict(order=self.order),
        )

    def remove_study_model(self) -> None:
        Study.objects.get(order=self.order).delete()

    def send_welcome_letter(self) -> None:
        if self.course.welcome_letter_template_id:
            send_mail.delay(
                to=self.user.email,
                template_id=self.course.welcome_letter_template_id,
                ctx=self.get_template_context(),
                disable_antispam=True,
            )

    def get_template_context(self) -> dict:
        return {
            "name": self.course.name,
            "slug": self.course.slug,
            "name_genitive": self.course.name_genitive,
        }
