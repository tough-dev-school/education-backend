import uuid
from mixer.backend.django import mixer

__all__ = [
    mixer,
]


mixer.register('users.User', username=lambda: str(uuid.uuid4()))
