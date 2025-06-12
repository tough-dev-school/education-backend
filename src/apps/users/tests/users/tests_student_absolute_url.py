from datetime import UTC, datetime
from urllib.parse import parse_qs, urlparse

import pytest

from apps.a12n.utils import decode_jwt_without_validation

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("_set_current_user"),
    pytest.mark.freeze_time("2032-12-01 15:30:30+03:00"),
]


@pytest.fixture(autouse=True)
def _set_frontend_url(settings):
    settings.FRONTEND_URL = "https://frontend:500"


@pytest.fixture
def student(mixer):
    return mixer.blend("users.Student")


def test_url(student):
    url = student.get_absolute_url()

    assert "https://frontend:500" in url
    assert f"/as/{student.pk}/" in url


def test_token(student, user):
    url = urlparse(student.get_absolute_url())
    query_string = parse_qs(url.query)
    token = query_string["t"][0]

    payload = decode_jwt_without_validation(token)

    assert payload["user_public_id"] == str(user.uuid), "Token is issued for the current user"
    assert str(datetime.fromtimestamp(payload["exp"], tz=UTC)) == "2032-12-01 12:35:30+00:00", "5 minutes from now"
