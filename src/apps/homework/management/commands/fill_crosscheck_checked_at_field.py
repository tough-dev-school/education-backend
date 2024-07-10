from django.core.management.base import BaseCommand
from django.db import transaction
from tqdm import tqdm

from apps.homework.models import Answer, AnswerCrossCheck


class Command(BaseCommand):
    help = "Fills checked_at field in AnswerCrossCheck with first answer date"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        queryset = AnswerCrossCheck.objects.all()
        total = queryset.count()

        for item in tqdm(queryset.iterator(), total=total):
            answer = Answer.objects.descendants(item.answer).filter(author=item.checker).first()
            item.checked_at = answer.created if answer else None
            item.save(update_fields=["checked_at"])
