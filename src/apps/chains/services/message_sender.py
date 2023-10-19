from dataclasses import dataclass
from functools import partial

from apps.chains import tasks
from apps.chains.models import Message
from apps.chains.models import Progress
from apps.mailing.tasks import send_mail
from apps.studying.models import Study
from core.services import BaseService


@dataclass
class MessageSender(BaseService):
    message: Message
    study: Study

    def act(self) -> bool:
        if not self.is_sent():
            self.send()
            return True

        return False

    def send(self) -> None:
        log_progress = partial(tasks.log_chain_progress.si, message_id=self.message.pk, study_id=self.study.pk)

        send_mail.apply_async(
            kwargs=dict(
                template_id=self.message.template_id,
                to=self.study.student.email,
                ctx=self.get_template_context(),
            ),
            link=log_progress(success=True),
            link_error=log_progress(success=False),
        )

    def is_sent(self) -> bool:
        return Progress.objects.filter(study_id=self.study.pk, message_id=self.message.pk).exists()

    def get_template_context(self) -> dict[str, str]:
        return {
            "firstname": self.study.student.first_name,
            "lastname": self.study.student.last_name,
        }
