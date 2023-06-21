from django.conf import settings

from app.tasks.dashamail import subscribe_to_dashamail
from users.models import User


def subscribe_user_to_dashamail(user: User, list_id: str | None = None, tags: list[str] | None = None) -> None:
    if not list_id:
        list_id = settings.DASHAMAIL_LIST_ID

    if not list_id:
        return

    subscribe_to_dashamail.delay(
        list_id=list_id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        tags=tags,
    )
