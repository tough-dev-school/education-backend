from dataclasses import dataclass
from typing import Callable

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


@dataclass
class Owl(BaseService):
    """Deliver messages [from Hogwarts] to the particular end-user"""

    to: str
    template_id: str
    subject: str | None = ""
    ctx: dict | None = None
    disable_antispam: bool | None = False

    force_configuration: EmailConfiguration | None = None
    max_retry_count: int = 1
    retry_attempt: int = 0

    def act(self) -> None:
        if not settings.EMAIL_ENABLED:
            return

        if self.is_sent_already and not self.disable_antispam:
            return

        self.send()

    def send(self) -> None:
        try:
            self.msg.send()
            self.write_email_log()
        except AnymailRequestsAPIError as e:
            self.process_exception(e)

    def process_exception(self, e: AnymailRequestsAPIError) -> None:
        if self.retry_attempt >= self.max_retry_count:
            raise e

        error_code = e.response.json().get("ErrorCode", None)
        processor = self._exception_processors.get(error_code, None)

        if processor is not None:
            return processor(e)

        raise e

    @property
    def _exception_processors(self) -> dict[int, Callable]:
        return {
            1101: self._template_not_found_exception,
        }

    def _template_not_found_exception(self, e: AnymailRequestsAPIError) -> None:
        Owl(
            to=self.to,
            template_id=self.template_id,
            subject=self.subject,
            ctx=self.ctx,
            force_configuration=self.get_default_configuration(),
            max_retry_count=self.max_retry_count,
            retry_attempt=self.retry_attempt + 1,
        )()

    def write_email_log(self) -> None:
        EmailLogEntry.objects.update_or_create(
            email=self.to,
            template_id=self.template_id,
        )

    @cached_property
    def msg(self) -> AnymailMessage:
        return AnymailMessage(
            subject=self.subject,
            body="",
            to=[self.to],
            connection=self.connection,
            from_email=self.configuration.from_email,
            reply_to=[self.configuration.reply_to],
            template_id=self.template_id,
            merge_global_data=self.normalized_message_context,
        )

    @property
    def connection(self) -> BaseEmailBackend:
        return mail.get_connection(
            fail_silently=False,
            backend=self.backend_name,
            **self.configuration.backend_options,
        )

    @property
    def normalized_message_context(self) -> dict:
        if self.ctx is None:
            return {}

        return helpers.normalize_email_context(self.ctx)

    @property
    def is_sent_already(self) -> bool:
        return EmailLogEntry.objects.filter(email=self.to, template_id=self.template_id).exists()

    @cached_property
    def configuration(self) -> EmailConfiguration:
        """
        Configuration works only in production mode to avoid confusing the developer when settings custom email backend
        """
        return self.force_configuration or get_configuration(recipient=self.to) or self.get_default_configuration()

    @cached_property
    def backend_name(self) -> str:
        if self.configuration.backend == EmailConfiguration.BACKEND.UNSET:
            return settings.EMAIL_BACKEND

        return self.configuration.backend

    @staticmethod
    def get_default_configuration() -> EmailConfiguration:
        return EmailConfiguration(
            backend=EmailConfiguration.BACKEND.UNSET,
            from_email=settings.DEFAULT_FROM_EMAIL,
            reply_to=settings.DEFAULT_REPLY_TO,
            backend_options={},
        )
