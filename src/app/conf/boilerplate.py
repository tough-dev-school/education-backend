import os.path

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ROOT_URLCONF = 'app.urls'

# Disable built-in ./manage.py test command in favor of pytest
TEST_RUNNER = 'app.test.disable_test_command_runner.DisableTestCommandRunner'

WSGI_APPLICATION = 'app.wsgi.application'
