from dataclasses import dataclass
from typing import final, TYPE_CHECKING

from app.services import BaseService
from app.tasks import update_dashamail_subscription
from users.tags.pipeline import apply_tags

if TYPE_CHECKING:
    from users.models import Student


@final
@dataclass
class TagsSynchronizer(BaseService):
    """
    Rebuild actual tags for student and update them to dashamail
    """

    student: "Student"
    list_id: str | None = None

    def act(self) -> None:
        apply_tags(self.student)
        update_dashamail_subscription.delay(user_id=self.student.pk, list_id=self.list_id)
