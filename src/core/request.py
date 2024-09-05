from threading import current_thread, local

from core.types import Request

_thread_locals = local()


def get_request() -> Request | None:
    return getattr(_thread_locals, _thread_key(), None)


def set_request(request: Request) -> None:
    setattr(_thread_locals, _thread_key(), request)


def unset_request() -> None:
    thread_key = _thread_key()

    if hasattr(_thread_locals, thread_key):
        delattr(_thread_locals, thread_key)


def _thread_key() -> str:
    thread_name = current_thread().name
    return f"request_{thread_name}"
