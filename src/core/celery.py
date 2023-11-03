import os

from celery import Celery
from celery.schedules import crontab

from django.conf import settings

from core.conf.environ import env

__all__ = [
    "celery",
]

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

celery = Celery("app")

celery.conf.update(
    broker_url=env("CELERY_BROKER_URL"),
    task_always_eager=env("CELERY_ALWAYS_EAGER", cast=bool, default=settings.DEBUG),  # by default in debug mode we run all celery tasks in foregroud.
    task_eager_propagates=True,
    task_ignore_result=True,
    task_store_errors_even_if_ignored=True,
    task_acks_late=True,
    task_routes={"apps.amocrm.tasks.*": {"queue": "amocrm"}},
    timezone=env("TIME_ZONE", cast=str, default="Europe/Moscow"),
    enable_utc=False,
    beat_schedule={
        "send_active_chains": {
            "task": "apps.chains.tasks.send_active_chains",
            "schedule": crontab(hour="*", minute="*/5"),
        },
        "amocrm_push_all_products_and_product_groups": {
            "task": "apps.amocrm.tasks.push_all_products_and_product_groups",
            "schedule": crontab(minute="15", hour="*/2"),
        },
    },
)


celery.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
