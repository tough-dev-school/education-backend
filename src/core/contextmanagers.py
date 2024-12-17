import os
from contextlib import contextmanager
from typing import Iterable


@contextmanager  # type: ignore
def modify_env(**update_vars: Iterable[tuple[str, str]]) -> None:  # type: ignore
    _environ = os.environ.copy()

    try:
        os.environ.update(update_vars)  # type: ignore
        yield
    finally:
        os.environ.clear()
        os.environ.update(_environ)
