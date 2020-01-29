from app.celery import celery
from orders.models import Order
from triggers import factory


@celery.task
def run_all_triggers():
    for trigger in factory.get_all_triggers():
        trigger.run()


@celery.task
def run_trigger(trigger_name, order_id):
    Trigger = factory.get(trigger_name)
    order = Order.objects.get(pk=order_id)

    Trigger(order)()
