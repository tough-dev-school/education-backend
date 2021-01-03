from django.apps import apps

from app.celery import celery


@celery.task
def test_task():
    apps.get_model('products.Course').objects.create(
        name='test_deffered',
        slug='sluuggsdftest',
    )
