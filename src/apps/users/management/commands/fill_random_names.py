from django.core.management import BaseCommand

from apps.users.models import User
from apps.users.random_name import random_name


class Command(BaseCommand):
    help = "(One-off) populate user db with the random names"

    def handle(self, *args, **kwargs):
        for user in User.objects.filter(random_name__isnull=True).iterator():
            user.random_name = random_name()

            user.save(update_fields=["random_name"])
