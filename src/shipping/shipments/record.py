from rest_framework import serializers

from courses.models import Record
from shipping import factory
from shipping.shipments.base import BaseShipment


class RecordTemplateContext(serializers.ModelSerializer):
    name_genitive = serializers.CharField(source='course.name_genitive')
    record_link = serializers.CharField(source='get_url')

    class Meta:
        model = Record
        fields = [
            'name_genitive',
            'record_link',
        ]


@factory.register(Record)
class RecordShipment(BaseShipment):
    template_id = 1069819

    @property
    def record(self):
        return self.stuff_to_ship

    def ship(self):
        self.send_email()

    def get_template_context(self) -> dict:
        return RecordTemplateContext().to_representation(self.record)
