from rest_framework import serializers

from app.tasks import invite_to_clickmeeting
from courses.models import Course
from shipping import factory
from shipping.shipments.base import BaseShipment


class CourseTemplateContext(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            'name',
            'name_genitive',
        ]


@factory.register(Course)
class CourseShipment(BaseShipment):

    @property
    def course(self):
        return self.stuff_to_ship

    def ship(self):
        self.invite()

    def invite(self):
        if self.course.clickmeeting_room_url is not None:
            invite_to_clickmeeting.delay(
                room_url=self.course.clickmeeting_room_url,
                email=self.user.email,
            )

    def get_template_context(self) -> dict:
        return CourseTemplateContext().to_representation(self.course)
