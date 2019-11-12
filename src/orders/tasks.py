from django.apps import apps

from app.celery import celery


@celery.task
def ship(order_id: int):
    order = apps.get_model('orders.Order').objects.get(pk=order_id)

    order.ship()
