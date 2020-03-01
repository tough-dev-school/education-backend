from app.celery import celery
from orders.models import Order
from triggers import factory


@celery.task
def run_all_triggers():
    for trigger in factory.get_all_triggers():
        for order_id in trigger.find_orders():
            run_trigger.delay(trigger.name, order_id)


@celery.task
def run_trigger(trigger_name, order_id):
    Trigger = factory.get(trigger_name)
    order = Order.objects.get(pk=order_id)

    Trigger(order)()
