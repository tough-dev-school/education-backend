from dataclasses import dataclass

from apps.chains.models import Chain, Message, Progress
from apps.studying.models import Study
from core.services import BaseService


@dataclass
class ChainSender(BaseService):
    chain: Chain

    def act(self) -> None:
        for study in Study.objects.filter(course=self.chain.course).iterator():
            self.send_messages_for_study(study)

    def send_messages_for_study(self, study: Study) -> None:
        self.send_root_messages(study)
        self.send_next_messages(study)

    def send_next_messages(self, study: Study) -> None:
        last_progress = Progress.objects.get_last_progress(study=study, chain=self.chain)

        if not last_progress:
            return

        next_message = Message.objects.filter(chain=self.chain, parent=last_progress.message).first()

        if next_message is not None and next_message.time_to_send(study=study):
            self.send(next_message, study=study)

    def send_root_messages(self, study: Study) -> None:
        for message in Message.objects.filter(chain=self.chain, parent__isnull=True):
            if not Progress.objects.filter(message=message, study=study).exists():
                self.send(message, study=study)

    @staticmethod
    def send(message: Message, study: Study) -> None:
        from apps.chains.services.message_sender import MessageSender

        MessageSender(message=message, study=study)()
