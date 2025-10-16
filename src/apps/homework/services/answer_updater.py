from dataclasses import dataclass
from typing import Callable

import simplejson as json
from django.contrib.admin.models import CHANGE
from django.db import transaction
from rest_framework.exceptions import NotAuthenticated, ValidationError

from apps.homework.models import Answer
from core.current_user import get_current_user
from core.prosemirror import ProseMirrorException, prosemirror_to_text
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
        self.write_auditlog(previous_content=previous_content)  # type: ignore [arg-type]
        return self.answer

    def get_validators(self) -> list[Callable]:
        return [
            self.validate_content_field,
            self.validate_content_is_prosemirror,
        ]

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

    def validate_content_field(self) -> None:
        if not isinstance(self.content, dict) or not len(self.content.keys()):
            raise ValidationError("Please provide content field")

    def validate_content_is_prosemirror(self) -> None:
        try:
            prosemirror_to_text(self.content)
        except ProseMirrorException:
            raise ValidationError("Not a prosemirror document")
