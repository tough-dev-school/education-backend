import pytest
from zoneinfo import ZoneInfo


@pytest.fixture
def kamchatka_timezone(settings) -> ZoneInfo:
    timezone_str = "Asia/Kamchatka"
    settings.TIME_ZONE = timezone_str
    return ZoneInfo(timezone_str)
