import pytest

from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture
def url(course):
    return f"/api/v2/users/?course={course.id}"


@pytest.mark.parametrize(
    ("requester", "expected"),
    [
        (pytest.lazy_fixture("client"), status.HTTP_401_UNAUTHORIZED),  # type: ignore[operator]
        (pytest.lazy_fixture("as_user"), status.HTTP_403_FORBIDDEN),  # type: ignore[operator]
    ],
)
def test_is_admin_user_permission(expected, requester, url):
    requester.get(url, expected_status_code=expected)


@pytest.mark.parametrize("method", ["delete", "patch", "put"])
def test_methods_not_allowed(as_superuser, method, url):
    getattr(as_superuser, method)(url, expected_status_code=status.HTTP_405_METHOD_NOT_ALLOWED)
