# type: ignore
from typing import List, Union

from django.conf import settings
from django.core.mail import EmailMessage

from app.mail import helpers
from app.models import EmailLogEntry


class TemplOwl:
    """This is a clone of the Owl class, with the same syntax, but supporting only template mailprovider messages.
    This class is not compatible for providers without templates, such as mailgun"""
    def __init__(self, to: Union[List, str], template_id, subject: str = '', ctx: dict = None, disable_antispam=False):
        if to in (None, [None]):
            to = []
        self.template_id = template_id
        self.subject = subject
        self.to = [to] if isinstance(to, str) else to
        self.ctx = helpers.normalize_email_context(ctx) if ctx is not None else {}

        if not disable_antispam:
            self.remove_spammed_emails()

        self.msg = self._get_message()

    def _get_message(self) -> EmailMessage:
        msg = EmailMessage(
            subject=self.subject,
            body='',
            to=self.to,
        )
        msg.template_id = self.template_id
        msg.merge_global_data = self.ctx
        return msg

    def send(self):
        if not settings.EMAIL_ENABLED:
            return

        self.msg.send()
        self.write_email_log()

    def attach(self, filename=None, content=None, mimetype=None):
        """Add an attachment to the message"""
        return self.msg.attach(filename, content, mimetype)

    def write_email_log(self):
        for email in self.to:
            EmailLogEntry.objects.update_or_create(
                email=email,
                template_id=self.template_id,
            )

    def remove_spammed_emails(self):
        self.to = [email for email in self.to if not EmailLogEntry.objects.filter(email=email, template_id=self.template_id).exists()]
