from app.celery import celery
from app.integrations import tg


@celery.task
def send_happiness_message(text):
    tg.send_happiness_message(text)
