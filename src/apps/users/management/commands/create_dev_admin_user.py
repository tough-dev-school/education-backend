from django.core.management import BaseCommand

from apps.users.models import User


class Command(BaseCommand):
    help = "create super admin with login root and password 123"

    def handle(self, *args, **kwargs):
        if User.objects.filter(username="root").exists():
            self.stdout.write(self.style.NOTICE("User root already exists, skipping"))
            return

        user = User.objects.create(
            username="root",
            email="root@localhost",
            is_staff=True,
            is_active=True,
            is_superuser=True,
        )

        user.set_password("123")
        user.save()

        self.stdout.write(self.style.SUCCESS('Created user with username "root" and password "123"'))
