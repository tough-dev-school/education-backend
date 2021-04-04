import pytest
from datetime import datetime

from a12n.models import PasswordlessAuthToken

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time('2049-01-05 12:45:44'),
]


def test(user):
    token = PasswordlessAuthToken.objects.create(user=user)

    assert '-4' in str(token.token)
    assert token.expires == datetime(2049, 1, 5, 14, 45, 44)
    assert token.used is False
