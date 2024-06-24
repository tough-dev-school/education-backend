from dataclasses import dataclass

from anymail.exceptions import AnymailRequestsAPIError
from anymail.message import AnymailMessage
from django.conf import settings
from django.core import mail
from django.core.mail.backends.base import BaseEmailBackend
from django.utils.functional import cached_property

from apps.mailing import helpers
from apps.mailing.configuration import get_configuration
from apps.mailing.models import EmailConfiguration, EmailLogEntry
from core.services import BaseService


class TemplateNotFoundError(AnymailRequestsAPIError): ...


@dataclass
class Owl(BaseService):
    """Deliver messages [from Hogwarts] to the particular end-user"""

    to: str
    template_id: str
    subject: str | None = ""
    ctx: dict | None = None
    disable_antispam: bool | None = False

    def act(self) -> None:
        if not settings.EMAIL_ENABLED:
            return

        if self.is_sent_already and not self.disable_antispam:
            return

        try:
            self.send(self.configuration)
        except TemplateNotFoundError as e:
            self._retry_with_default_configuration(e)

    def send(self, configuration: "EmailConfiguration") -> None:
        message = self.get_message(configuration)

        try:
            message.send()
            self.write_email_log()
        except AnymailRequestsAPIError as e:
            self.anymail_exception_handler(e)

    @staticmethod
    def get_connection(configuration: "EmailConfiguration") -> BaseEmailBackend:
        return mail.get_connection(
            fail_silently=False,
            backend=configuration.backend_name,
            **configuration.backend_options,
        )

    def get_message(self, configuration: "EmailConfiguration") -> AnymailMessage:
        return AnymailMessage(
            subject=self.subject,
            body="",
            to=[self.to],
            connection=self.get_connection(configuration),
            from_email=configuration.from_email,
            reply_to=[configuration.reply_to],
            template_id=self.template_id,
            merge_global_data=self.normalized_message_context,
        )

    def _retry_with_default_configuration(self, error: "TemplateNotFoundError") -> None:
        if self.configuration == self.default_configuration:
            raise error

        self.send(self.default_configuration)

    @cached_property
    def configuration(self) -> EmailConfiguration:
        return get_configuration(recipient=self.to) or self.default_configuration

    @cached_property
    def default_configuration(self) -> EmailConfiguration:
        return EmailConfiguration(
            backend=EmailConfiguration.BACKEND.UNSET,
            from_email=settings.DEFAULT_FROM_EMAIL,
            reply_to=settings.DEFAULT_REPLY_TO,
            backend_options={},
        )

    @property
    def normalized_message_context(self) -> dict:
        if self.ctx is None:
            return {}

        return helpers.normalize_email_context(self.ctx)

    @property
    def is_sent_already(self) -> bool:
        return EmailLogEntry.objects.filter(email=self.to, template_id=self.template_id).exists()

    def write_email_log(self) -> None:
        EmailLogEntry.objects.update_or_create(
            email=self.to,
            template_id=self.template_id,
        )

    @staticmethod
    def anymail_exception_handler(exception: AnymailRequestsAPIError) -> None:
        error_code = exception.response.json().get("ErrorCode", None)

        if error_code == 1101:
            raise TemplateNotFoundError(exception)

        raise exception
