import uuid
from hattori.base import BaseAnonymizer, faker

from a12n.models import PasswordlessAuthToken


class PassworlessAuthTokenAnonizdr(BaseAnonymizer):
    model = PasswordlessAuthToken

    attributes = [
        ('created', faker.date),
        ('modified', faker.date),
        ('expires', faker.date),
        ('used', faker.date),
    ]

    def run(self, *args, **kwargs):
        result = super().run(*args, **kwargs)

        self.replace_tokens()

        return result

    def replace_tokens(self):
        """Need this method cuz hattori cant handle uuids"""
        for instance in self.get_query_set().iterator():
            instance.token = uuid.uuid4()
            instance.save()
