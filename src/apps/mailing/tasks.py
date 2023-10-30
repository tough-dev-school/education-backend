from anymail.exceptions import AnymailRequestsAPIError

from apps.mailing.owl import Owl
from core.celery import celery


@celery.task(
    autoretry_for=[AnymailRequestsAPIError],
    retry_kwargs={
        "max_retries": 10,
        "countdown": 5,
    },
    acks_late=True,
)
def send_mail(to: str, template_id: str, subject: str | None = "", ctx: dict | None = None, disable_antispam: bool | None = False) -> None:
    Owl(
        to=to,
        template_id=template_id,
        subject=subject,
        ctx=ctx,
        disable_antispam=disable_antispam,
    )()
