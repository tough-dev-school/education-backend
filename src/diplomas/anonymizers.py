import shortuuid
from hattori.base import BaseAnonymizer, faker

from diplomas.models import Diploma


class EmailLogEntryAnonymizer(BaseAnonymizer):
    model = Diploma

    attributes = [
        ('created', faker.date),
        ('modified', faker.date),
        ('slug', shortuuid.uuid),
        ('image', lambda: f'{faker.uri_path()}.jpg'),
    ]
