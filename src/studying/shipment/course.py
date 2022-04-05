from typing import Optional

from app.tasks import (
    invite_to_clickmeeting, invite_to_zoomus, send_mail, subscribe_to_dashamail, unsubscribe_from_dashamail)
from products.models import Course
from studying import shipment_factory as factory
from studying.models import Study
from studying.shipment.base import BaseShipment


@factory.register(Course)
class CourseShipment(BaseShipment):
    @property
    def course(self):
        return self.stuff_to_ship

    def ship(self) -> None:
        self.invite_to_clickmeeting()
        self.invite_to_zoomus()
        self.subscribe_to_dashamail()
        self.create_study_model()

        self.send_welcome_letter()

    def unship(self) -> None:
        self.remove_study_model()
        self.unsubscribe_from_dashamail()

    def create_study_model(self) -> None:
        Study.objects.get_or_create(
            course=self.course,
            student=self.user,
            defaults=dict(order=self.order),
        )

    def remove_study_model(self) -> None:
        Study.objects.get(order=self.order).delete()

    def subscribe_to_dashamail(self) -> None:
        if self.course.dashamail_list_id is not None:
            subscribe_to_dashamail.delay(
                list_id=self.course.dashamail_list_id,
                user_id=self.user.pk,
                tags=[self.course.slug, f'{self.course.slug}-purchased'],
            )

    def unsubscribe_from_dashamail(self) -> None:
        if self.course.dashamail_list_id is not None:
            unsubscribe_from_dashamail.delay(
                list_id=self.course.dashamail_list_id,
                user_id=self.user.pk,
            )

    def invite_to_clickmeeting(self) -> None:
        if self.course.clickmeeting_room_url is not None:
            invite_to_clickmeeting.delay(
                room_url=self.course.clickmeeting_room_url,
                email=self.user.email,
            )

    def invite_to_zoomus(self) -> None:
        if self.course.zoomus_webinar_id is not None and len(self.course.zoomus_webinar_id):
            invite_to_zoomus.delay(
                webinar_id=self.course.zoomus_webinar_id,
                user_id=self.user.id,
            )

    def send_welcome_letter(self) -> None:
        if self.welcome_letter_template_id is not None:
            send_mail.delay(
                to=self.user.email,
                template_id=self.welcome_letter_template_id,
                ctx=self.get_template_context(),
                disable_antispam=True,
            )

    def get_template_context(self) -> dict:
        return {
            'name': self.course.name,
            'slug': self.course.slug,
            'name_genitive': self.course.name_genitive,
            **self.get_gift_template_context(),
        }

    @property
    def welcome_letter_template_id(self) -> Optional[str]:
        """Get special gift template letter id if order is a gift and it is present"""
        template_id = self.course.welcome_letter_template_id

        if self.order.giver is not None:  # this is a gift
            template_id = self.course.gift_welcome_letter_template_id or self.course.welcome_letter_template_id

        if template_id is None or not len(template_id):  # fuck this null=True in CharFields
            return None

        return template_id
