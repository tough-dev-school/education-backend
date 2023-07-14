# type: ignore
from django.core.management.base import BaseCommand

from users.tasks import rebuild_tags_for_all_students


class Command(BaseCommand):
    help = "Update tags for all active users who is active and not staff"

    def handle(self, *args, **options):
        rebuild_tags_for_all_students.delay()
        self.stdout.write("Task is created. Tags will be updated soon.")
