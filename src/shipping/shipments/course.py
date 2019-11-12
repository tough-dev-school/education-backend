from rest_framework import serializers

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
    template_id = 100500

    @property
    def course(self):
        return self.stuff_to_ship

    def ship(self):
        self.invite()
        self.send_email()

    def invite(self):
        pass

    def get_template_context(self) -> dict:
        return CourseTemplateContext().to_representation(self.course)
