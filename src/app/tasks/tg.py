from app.celery import celery
from app.integrations import tg


@celery.task
def send_happiness_message(text: str) -> None:
    tg.send_happiness_message(text)
