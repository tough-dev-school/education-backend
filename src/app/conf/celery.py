from celery.schedules import crontab

from app.conf.environ import env

broker_url = env('CLOUDAMQP_URL')
task_always_eager = env('CELERY_ALWAYS_EAGER', cast=bool, default=env('DEBUG'))  # by default in debug mode we run all celery tasks in foregroud.
timezone = env('TIME_ZONE', cast=str, default='Europe/Moscow')
enable_utc = False
beat_schedule = {
    'run_started_purchase_trigger': {
        'task': 'triggers.tasks.check_for_started_purchase_triggers',
        'schedule': crontab(hour='*', minute=15),
    },
    'run_record_feedback_trigger': {
        'task': 'triggers.tasks.check_for_record_feedback_triggers',
        'schedule': crontab(hour='*', minute=15),
    },
    'ship_unshipped_orders': {
        'task': 'orders.tasks.ship_unshipped_orders',
        'schedule': crontab(hour='*', minute='*/2'),
    },
}
