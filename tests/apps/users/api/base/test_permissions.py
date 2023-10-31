import pytest

from rest_framework import status

pytestmark = pytest.mark.django_db

url = "/api/v2/users/"


@pytest.mark.parametrize(
    ("requester", "expected"),
    [
        (pytest.lazy_fixture("anon"), status.HTTP_401_UNAUTHORIZED),  # type: ignore[operator]
        (pytest.lazy_fixture("as_user"), status.HTTP_403_FORBIDDEN),  # type: ignore[operator]
    ],
)
def test_is_admin_user_permission(expected, requester):
    requester.get(url, expected_status_code=expected)


@pytest.mark.parametrize("method", ["delete", "patch", "put"])
def test_methods_not_allowed(as_superuser, method):
    getattr(as_superuser, method)(url, expected_status_code=status.HTTP_405_METHOD_NOT_ALLOWED)
