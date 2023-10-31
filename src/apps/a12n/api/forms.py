from typing import Any
from urllib.parse import urljoin

from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm as DjangoPasswordResetForm

from apps.mailing.tasks import send_mail


class EspTemplatePasswordResetForm(DjangoPasswordResetForm):
    """Same as Django's password reset form but use ESP template for email."""

    def get_reset_url(self, context: dict[str, Any]) -> str:
        # reset url is similar to django's `registration/password_reset_email.html` template
        return urljoin(
            settings.FRONTEND_URL,
            "/".join(["auth", "password", "reset", context["uid"], context["token"], ""]),
        )

    def send_mail(
        self,
        subject_template_name: str,
        email_template_name: str,
        context: dict[str, Any],
        from_email: str | None,
        to_email: str,
        html_email_template_name: str | None = None,
    ) -> None:
        send_mail.delay(
            to=to_email,
            template_id=settings.PASSWORD_RESET_TEMPLATE_ID,
            ctx={
                "name": context["user"].get_full_name(),
                "email": to_email,
                "action_url": self.get_reset_url(context),
            },
            disable_antispam=True,
        )
