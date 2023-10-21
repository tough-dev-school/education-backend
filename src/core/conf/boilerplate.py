from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

ROOT_URLCONF = "core.urls"

# Disable built-in ./manage.py test command in favor of pytest
TEST_RUNNER = "core.test.disable_test_command_runner.DisableTestCommandRunner"

WSGI_APPLICATION = "core.wsgi.application"
