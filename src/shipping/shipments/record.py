from rest_framework import serializers

from app.tasks import send_mail
from courses.models import Record
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


class RecordShipment(BaseShipment):
    @property
    def record(self):
        return self.stuff_to_ship

    def ship(self):
        self.send_email()

    def send_email(self):
        return send_mail.delay(
            to=self.user.email,
            template_id=1069819,
            ctx=self.get_template_context(),
        )

    def get_template_context(self) -> dict:
        return RecordTemplateContext().to_representation(self.record)
