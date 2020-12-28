import pytest
from datetime import datetime

pytestmark = [pytest.mark.django_db]


@pytest.mark.freeze_time('2032-12-01 15:30')
def test_expires_when_updated(token):
    token.download()

    token.refresh_from_db()

    assert token.expires == datetime(2032, 12, 3, 15, 30)
