import os

from core.contextmanagers import modify_env


def test_modify_env(monkeypatch):
    monkeypatch.setenv("SOME_ENV_VAR", "initial_value")

    with modify_env(SOME_ENV_VAR="new_value"):
        assert os.environ["SOME_ENV_VAR"] == "new_value"

    assert os.environ["SOME_ENV_VAR"] == "initial_value"
