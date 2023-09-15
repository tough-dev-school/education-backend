import httpx

from django.conf import settings


def send_message(chat_id: str, text: str) -> None:
    url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage"
    response = httpx.post(
        url,
        data={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "markdown",
            "disable_web_page_preview": True,
        },
    )

    assert response.status_code == 200, "TG should return 200"
