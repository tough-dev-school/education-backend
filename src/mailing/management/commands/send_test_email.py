from django.core.management.base import BaseCommand

from mailing import tasks


class Command(BaseCommand):
    def add_arguments(self, parser) -> None:
        parser.add_argument("--email", type=str, required=True, help="Destination email")
        parser.add_argument("--template_id", type=str, required=True, help="Postmark template id")

    def handle(self, *args, email: str, template_id: str, **options) -> None:
        tasks.send_mail(
            to=email,
            template_id=template_id,
        )

        self.stdout.write(self.style.SUCCESS(f'Sent email with template_id "{template_id}" to "{email}"'))
