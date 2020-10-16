from rest_framework import serializers

from app.tasks import invite_to_clickmeeting, invite_to_zoomus, send_mail
from courses.models import Course
from shipping import factory
from shipping.shipments.base import BaseShipment


class CourseTemplateContext(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            'name',
            'slug',
            'name_genitive',
        ]


@factory.register(Course)
class CourseShipment(BaseShipment):

    @property
    def course(self):
        return self.stuff_to_ship

    def ship(self):
        self.invite_to_clickmeeting()
        self.invite_to_zoomus()
        self.send_welcome_letter()

    def invite_to_clickmeeting(self):
        if self.course.clickmeeting_room_url is not None:
            invite_to_clickmeeting.delay(
                room_url=self.course.clickmeeting_room_url,
                email=self.user.email,
            )

    def invite_to_zoomus(self):
        if self.course.zoomus_webinar_id is not None and len(self.course.zoomus_webinar_id):
            invite_to_zoomus.delay(
                webinar_id=self.course.zoomus_webinar_id,
                user_id=self.user.id,
            )

    def send_welcome_letter(self):
        if self.course.welcome_letter_template_id is not None and len(self.course.welcome_letter_template_id):
            send_mail.delay(
                to=self.user.email,
                template_id=self.course.welcome_letter_template_id,
                ctx=self.get_template_context(),
                disable_antispam=True,
            )

    def get_template_context(self) -> dict:
        return CourseTemplateContext().to_representation(self.course)
