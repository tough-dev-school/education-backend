from django.conf import settings
from django.core.management.commands.startapp import Command as BaseCommand


class Command(BaseCommand):
    def handle(self, **options):
        directory = settings.BASE_DIR.parent / "apps" / options["name"]
        directory.mkdir()

        options.update(directory=str(directory))

        super().handle(**options)
