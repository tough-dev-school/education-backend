from typing import List, Union

from anymail.exceptions import AnymailRequestsAPIError

from app.celery import celery
from app.mail.owl import TemplOwl


@celery.task(
    autoretry_for=[AnymailRequestsAPIError],
    retry_kwargs={
        'max_retries': 10,
        'countdown': 5,
    },
)
def send_mail(to: Union[List, str], template_id, subject: str = '', ctx: dict = None, disable_antispam=False):
    TemplOwl(
        to=to,
        template_id=template_id,
        subject=subject,
        ctx=ctx,
        disable_antispam=disable_antispam,
    ).send()
