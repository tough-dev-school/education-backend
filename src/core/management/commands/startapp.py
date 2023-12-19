from typing import TYPE_CHECKING

from django.conf import settings
from django.core.management.commands.startapp import Command as BaseCommand

if TYPE_CHECKING:
    from typing import Any


class Command(BaseCommand):
    def handle(self, **options: "Any") -> None:  # type: ignore[override]
        directory = settings.BASE_DIR.parent / "apps" / options["name"]
        directory.mkdir()

        options.update(directory=str(directory))

        super().handle(**options)
