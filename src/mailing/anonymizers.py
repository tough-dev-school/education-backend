
from hattori.base import BaseAnonymizer, faker

from mailing.models import EmailLogEntry


class EmailLogEntryAnonymizer(BaseAnonymizer):
    model = EmailLogEntry

    attributes = [
        ('created', faker.date),
        ('email', faker.email),
        ('template_id', lambda: '-'.join(faker.words(nb=5))),
    ]
