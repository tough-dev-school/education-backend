from dataclasses import dataclass
from typing import final, TYPE_CHECKING

from app.integrations.dashamail.helpers import subscribe_user_to_dashamail
from app.services import BaseService
from users.tags.pipeline import apply_tags

if TYPE_CHECKING:
    from users.models import Student


@final
@dataclass
class TagsSynchronizer(BaseService):
    """
    Rebuild actual tags for student and send them to dashamail
    """

    student: "Student"
    list_id: str | None = None

    def act(self) -> None:
        apply_tags(self.student)
        subscribe_user_to_dashamail(user=self.student, tags=self.student.tags, list_id=self.list_id)
