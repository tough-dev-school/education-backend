from django.core.management.base import BaseCommand
from django.db import transaction
from tqdm import tqdm

from apps.homework.models import Answer, AnswerCrossCheck


class Command(BaseCommand):
    help = "Denormalizes is_checked field in AnswerCrossCheck"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        queryset = AnswerCrossCheck.objects.all()
        total = queryset.count()

        for item in tqdm(queryset.iterator(), total=total):
            item.is_checked = Answer.objects.descendants(item.answer).filter(author=item.checker).exists()
            item.save(update_fields=["is_checked"])
