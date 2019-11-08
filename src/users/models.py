from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    @classmethod
    def parse_name(cls, name: str) -> dict:
        parts = name.split(' ', 2)

        if len(parts) == 1:
            return {'first_name': parts[0]}

        if len(parts) == 2:
            return {'first_name': parts[0], 'last_name': parts[1]}

        return {'first_name': parts[0], 'last_name': ' '.join(parts[1:])}
