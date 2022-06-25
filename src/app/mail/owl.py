from anymail.message import AnymailMessage
from dataclasses import dataclass
from django.conf import settings
from django.utils.functional import cached_property

from app.mail import helpers
from app.models import EmailLogEntry


@dataclass
class Owl:
    """Deliver messages [from Hogwarts] to end-users
    """
    to: str
    template_id: str
    subject: str | None = ''
    ctx: dict | None = None
    disable_antispam: bool | None = False

    def __call__(self) -> None:
        if not settings.EMAIL_ENABLED:
            return

        if not self.disable_antispam and self.is_sent_already():
            return

        self.msg.send()
        self.write_email_log()

    @cached_property
    def msg(self) -> AnymailMessage:
        msg = AnymailMessage(
            subject=self.subject,
            body='',
            to=[self.to],
        )
        msg.template_id = self.template_id
        msg.merge_global_data = self.get_normalized_message_context()

        return msg

    def attach(self, filename=None, content=None, mimetype=None):
        """Add an attachment to the message"""
        return self.msg.attach(filename, content, mimetype)

    def get_normalized_message_context(self) -> dict:
        if self.ctx is None:
            return {}

        return helpers.normalize_email_context(self.ctx)

    def write_email_log(self) -> None:
        EmailLogEntry.objects.update_or_create(
            email=self.to,
            template_id=self.template_id,
        )

    def is_sent_already(self) -> bool:
        return EmailLogEntry.objects.filter(email=self.to, template_id=self.template_id).exists()
