from django.conf import settings

from app.tasks.dashamail import manage_subscription_to_dashamail
from users.models import User


def manage_users_subscription_to_dashamail(user: User, tags: list[str], list_id: str | None = None) -> None:
    if not list_id:
        list_id = settings.DASHAMAIL_LIST_ID

    if not list_id:
        return

    manage_subscription_to_dashamail.delay(
        list_id=list_id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        tags=tags,
    )
