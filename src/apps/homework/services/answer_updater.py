from dataclasses import dataclass

import simplejson as json
from django.contrib.admin.models import CHANGE
from django.db import transaction
from rest_framework.exceptions import NotAuthenticated

from apps.homework.models import Answer
from core.current_user import get_current_user
from core.prosemirror import prosemirror_to_text
from core.services import BaseService
from core.tasks.write_admin_log import write_admin_log


@dataclass
class AnswerUpdater(BaseService):
    answer: Answer
    content: dict

    @transaction.atomic
    def act(self) -> Answer:
        previous_content = self.answer.content

        self.update()
        self.write_auditlog(previous_content=previous_content)
        return self.answer

    def update(self) -> None:
        self.answer.content = self.content
        self.answer.text = prosemirror_to_text(self.content)
        self.answer.save(update_fields=["content", "text", "modified"])

    def write_auditlog(self, previous_content: dict) -> None:
        previous = json.dumps(previous_content, ensure_ascii=False)
        current = json.dumps(self.answer.content, ensure_ascii=False)

        user = get_current_user()
        if user is None:
            raise NotAuthenticated()

        write_admin_log.delay(
            action_flag=CHANGE,
            app="homework",
            change_message=f"Answer content updated. Previous: {previous}. Current: {current}.",
            model="Answer",
            object_id=self.answer.id,
            user_id=user.id,
        )
