import pytest
from django.core import mail

pytestmark = [pytest.mark.django_db]


def test_sending(owl) -> None:
    owl()()

    assert len(mail.outbox) == 1


@pytest.mark.parametrize(
    "switch",
    [
        lambda settings: setattr(settings, "EMAIL_ENABLED", False),
    ],
)
def test_kill_switch(owl, switch, settings) -> None:
    switch(settings)

    owl()()

    assert len(mail.outbox) == 0
