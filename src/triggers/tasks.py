from datetime import timedelta

from django.utils import timezone

from app.celery import celery
from orders.models import Order
from triggers import factory
from triggers.started_purchase import StartedPurchaseTrigger


@celery.task
def run_started_purchase_trigger(order_id):
    order = Order.objects.get(pk=order_id)

    StartedPurchaseTrigger(order)()


@celery.task
def check_for_started_purchase_triggers():
    for order in Order.objects.filter(paid__isnull=True, created__gte=timezone.now() - timedelta(days=3)).iterator():
        run_started_purchase_trigger.delay(order.pk)


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
