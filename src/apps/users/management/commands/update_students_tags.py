# type: ignore
from django.apps import apps
from django.core.management.base import BaseCommand

from apps.users.tasks import rebuild_tags


class Command(BaseCommand):
    help = "Update tags for all active users who is active and not staff"

    def handle(self, *args, **options):
        student_ids = apps.get_model("users.Student").objects.filter(is_active=True, is_staff=False).exclude(email="").values_list("pk", flat=True)
        for student_id in student_ids:
            rebuild_tags.delay(student_id)
        self.stdout.write("Task is created. Tags will be updated soon.")
