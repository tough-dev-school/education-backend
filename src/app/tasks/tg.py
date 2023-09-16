from app.celery import celery
from app.integrations import tg


@celery.task
def send_telegram_message(chat_id: str, text: str) -> None:
    tg.send_message(chat_id=chat_id, text=text)
