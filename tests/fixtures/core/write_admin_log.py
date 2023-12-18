import pytest


@pytest.fixture
def write_admin_log(mocker):
    return mocker.patch("core.tasks.write_admin_log.delay")
