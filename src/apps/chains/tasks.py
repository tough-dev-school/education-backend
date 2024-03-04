from apps.chains.models import Chain, Progress
from apps.chains.services import ChainSender
from core.celery import celery


@celery.task
def send_active_chains() -> None:
    for chain in Chain.objects.active():
        send_chain_messages.delay(chain.pk)


@celery.task
def send_chain_messages(chain_id: int) -> None:
    chain = Chain.objects.get(pk=chain_id)

    ChainSender(chain)()


@celery.task(acks_late=True)
def log_chain_progress(*, message_id: int, study_id: int, success: bool) -> None:
    Progress.objects.create(message_id=message_id, study_id=study_id, success=success)
