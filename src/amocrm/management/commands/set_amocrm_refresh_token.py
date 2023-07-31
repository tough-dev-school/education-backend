from django.core.cache import cache
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Set in cache refresh token for amocrm"

    def add_arguments(self, parser):
        parser.add_argument("refresh_token", nargs="+", type=str, help="refresh_token for getting access token")

    def handle(self, *args, **kwargs):
        refresh_token = kwargs["refresh_token"]

        cache.set("amocrm_refresh_token", refresh_token)

        self.stdout.write(self.style.SUCCESS("Refresh token is set."))
