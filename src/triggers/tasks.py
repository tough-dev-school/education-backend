from datetime import timedelta

from django.utils import timezone

from app.celery import celery
from orders.models import Order
from triggers.factory import get_all_triggers, run
from triggers.record_feedback import RecordFeedbackTrigger
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
def run_record_feedback_trigger(order_id):
    order = Order.objects.get(pk=order_id)

    RecordFeedbackTrigger(order)()


@celery.task
def check_for_record_feedback_triggers():
    for order in Order.objects.filter(paid__isnull=False, record__isnull=False, created__gte=timezone.now() - timedelta(days=6)).iterator():
        run_record_feedback_trigger.delay(order.pk)


@celery.task
def run_all_triggers():
    for trigger in get_all_triggers():
        trigger.run()


@celery.task
def run_trigger(trigger_name, order_id):
    order = Order.objects.get(pk=order_id)

    run(trigger_name, order)
