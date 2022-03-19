from app.celery import celery
from chains.models import Chain
from chains.services import ChainSender


@celery.task
def send_active_chains():
    for chain in Chain.objects.active():
        send_chain_messages.delay(chain.pk)


@celery.task
def send_chain_messages(chain_id: int):
    chain = Chain.objects.get(pk=chain_id)

    ChainSender(chain)()
