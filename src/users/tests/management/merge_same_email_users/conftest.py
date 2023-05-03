from datetime import datetime
import pytest

from users.management.commands import merge_same_email_users
from users.models import User


@pytest.fixture
def bob_a(mixer, kamchatka_timezone) -> User:
    return mixer.blend(
        "users.User",
        username="boB@EXAMPLE.com",
        email="boB@EXAMPLE.com",
        date_joined=datetime(2021, 11, 1, tzinfo=kamchatka_timezone),
    )


@pytest.fixture
def bob_b(mixer, kamchatka_timezone) -> User:
    return mixer.blend(
        "users.User",
        username="Bob@Example.Com",
        email="Bob@Example.Com",
        date_joined=datetime(2021, 11, 2, tzinfo=kamchatka_timezone),
    )


@pytest.fixture
def bob_c(mixer, kamchatka_timezone) -> User:
    return mixer.blend(
        "users.User",
        username="BOB@EXAMPLE.COM",
        email="BOB@EXAMPLE.COM",
        date_joined=datetime(2021, 11, 3, tzinfo=kamchatka_timezone),
    )


@pytest.fixture
def command():
    return merge_same_email_users.Command()
