from threading import current_thread
from threading import local

from users.models import User

_thread_locals = local()


def get_current_user() -> User | None:
    user = getattr(_thread_locals, _thread_key(), None)
    if user is not None and user.is_authenticated:
        return user


def set_current_user(user: User) -> None:
    setattr(_thread_locals, _thread_key(), user)


def unset_current_user() -> None:
    thread_key = _thread_key()

    if hasattr(_thread_locals, thread_key):
        delattr(_thread_locals, thread_key)


def _thread_key() -> str:
    thread_name = current_thread().name
    return f"user_{thread_name}"
