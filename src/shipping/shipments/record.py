from rest_framework import serializers

from app.tasks import send_mail
from courses.models import Record
from shipping import factory
from shipping.shipments.base import BaseShipment


class RecordTemplateContext(serializers.ModelSerializer):
    record_link = serializers.CharField(source='get_url')

    class Meta:
        model = Record
        fields = [
            'name_genitive',
            'record_link',
        ]


@factory.register(Record)
class RecordShipment(BaseShipment):
    template_id = 'purchased-record'

    @property
    def record(self):
        return self.stuff_to_ship

    def ship(self):
        self.send_record_link()

    def get_template_context(self) -> dict:
        return RecordTemplateContext().to_representation(self.record)

    def send_record_link(self):
        """Send email, convinience method for subclasses

        The mail is not sent by default, you have to call it manualy!
        """
        return send_mail.delay(
            to=self.user.email,
            template_id=self.get_template_id(),
            ctx=self.get_template_context(),
        )

    def get_template_id(self):
        template_id = self.record.get_template_id()

        if template_id is not None:
            return template_id

        return self.template_id

    def get_template_context(self) -> dict:
        return RecordTemplateContext().to_representation(self.record)
