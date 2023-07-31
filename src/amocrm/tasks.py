from amocrm.client import AmoCRMClient
from amocrm.models import AmoCRMUser
from app.celery import celery
from users.models import User

client = AmoCRMClient()


@celery.task
def create_customer(user_id: int) -> int:
    user = User.objects.get(id=user_id)
    return client.create_customer(user=user)


@celery.task
def update_customer(amocrm_user_id: int) -> int:
    amocrm_user = AmoCRMUser.objects.get(amocrm_id=amocrm_user_id)
    return client.update_customer(amocrm_user=amocrm_user)
