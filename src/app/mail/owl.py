from typing import List, Union

from django.conf import settings
from django.core.mail import EmailMessage

from app.mail import helpers


class TemplOwl:
    """This is a clone of the Owl class, with the same syntax, but supporting only template mailprovider messages.
    This class is not compatible for providers without templates, such as mailgun"""
    def __init__(self, to: Union[List, str], template_id, subject: str = '', ctx: dict = None):
        if to in (None, [None]):
            to = []
        self.template_id = template_id
        self.subject = subject
        self.to = [to] if isinstance(to, str) else to
        self.ctx = helpers.normalize_email_context(ctx) if ctx is not None else dict()
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
        if settings.EMAIL_ENABLED:
            return self.msg.send()

    def attach(self, filename=None, content=None, mimetype=None):
        """Add an attachment to the message"""
        return self.msg.attach(filename, content, mimetype)
