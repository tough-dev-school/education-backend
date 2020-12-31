import uuid
from mixer.backend.django import mixer

__all__ = [
    mixer,
]


@mixer.middleware('users.User')
def make_username_truly_random(user):
    user.username = str(uuid.uuid4())

    return user
