from django.apps import apps
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Clean antispam logs for outgoing email and marketing triggers"

    def handle(self, *args, **kwargs):
        app_wide = apps.get_model("core.EmailLogEntry").objects.all().delete()[0]
        marketing = apps.get_model("triggers.TriggerLogEntry").objects.all().delete()[0]

        self.stdout.write(self.style.SUCCESS(f"Removed {app_wide} email log entries and {marketing} marketing trigger log entries."))
