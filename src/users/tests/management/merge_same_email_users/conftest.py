import pytest
from datetime import datetime
from django.conf import settings
from zoneinfo import ZoneInfo

from users.management.commands import merge_same_email_users
from users.models import User


@pytest.fixture
def bob_a(mixer) -> User:
    return mixer.blend(
        'users.User',
        username='boB@EXAMPLE.com',
        email='boB@EXAMPLE.com',
        date_joined=datetime(2021, 11, 1, tzinfo=ZoneInfo(settings.TIME_ZONE)),
    )


@pytest.fixture
def bob_b(mixer) -> User:
    return mixer.blend(
        'users.User',
        username='Bob@Example.Com',
        email='Bob@Example.Com',
        date_joined=datetime(2021, 11, 2, tzinfo=ZoneInfo(settings.TIME_ZONE)),
    )


@pytest.fixture
def bob_c(mixer) -> User:
    return mixer.blend(
        'users.User',
        username='BOB@EXAMPLE.COM',
        email='BOB@EXAMPLE.COM',
        date_joined=datetime(2021, 11, 3, tzinfo=ZoneInfo(settings.TIME_ZONE)),
    )


@pytest.fixture
def command():
    return merge_same_email_users.Command()
