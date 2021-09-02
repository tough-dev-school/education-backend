from hattori.base import BaseAnonymizer, faker

from diplomas.models import Diploma


class DiplomaAnonymizer(BaseAnonymizer):
    model = Diploma

    attributes = [
        ('created', faker.date),
        ('modified', faker.date),
        ('slug', faker.slug),
    ]
