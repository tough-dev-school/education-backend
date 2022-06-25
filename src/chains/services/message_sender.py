from dataclasses import dataclass
from functools import partial

from chains import tasks
from chains.models import Message, Progress
from mailing.tasks import send_mail
from studying.models import Study


@dataclass
class MessageSender:
    message: Message
    study: Study

    def __call__(self) -> bool:
        if not self.is_sent():
            self.send()
            return True

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
            'firstname': self.study.student.first_name,
            'lastname': self.study.student.last_name,
        }
