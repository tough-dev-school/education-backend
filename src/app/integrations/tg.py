import requests

from django.conf import settings


def send_message(channel: str, text: str) -> None:
    url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage"
    response = requests.post(
        url,
        data={
            "chat_id": channel,
            "text": text,
            "parse_mode": "markdown",
            "disable_web_page_preview": True,
        },
    )

    assert response.status_code == 200, "TG should return 200"


def send_happiness_message(text: str) -> None:
    send_message(settings.HAPPINESS_MESSAGES_CHAT_ID, text)
