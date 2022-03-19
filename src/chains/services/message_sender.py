from celery import chain
from dataclasses import dataclass

from app.tasks import send_mail
from chains import tasks
from chains.models import Message, Progress
from studying.models import Study


@dataclass
class MessageSender:
    message: Message
    study: Study

    def __call__(self) -> bool:
        if not self.is_sent():
            self.send()
            return True

        return False

    def send(self) -> None:
        task = chain(
            send_mail.s(
                template_id=self.message.template_id,
                to=self.study.student.email,
                ctx=self.get_template_context(),
            ),
            tasks.log_chain_progress.s(message_id=self.message.id, study_id=self.study.id),
        )

        task.delay()

    def is_sent(self) -> bool:
        return Progress.objects.filter(study=self.study, message=self.message).exists()

    def get_template_context(self) -> dict[str, str]:
        return {
            'firstname': self.study.student.first_name,
            'lastname': self.study.student.last_name,
        }
