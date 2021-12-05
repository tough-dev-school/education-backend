import uuid
from mixer.backend.django import mixer

mixer.register('users.User', username=lambda: str(uuid.uuid4()))

__all__ = [
    'mixer',
]
