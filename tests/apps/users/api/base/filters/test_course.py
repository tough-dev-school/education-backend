import pytest

pytestmark = pytest.mark.django_db


@pytest.fixture
def course(factory, user):
    return factory.course(id=1)


@pytest.fixture
def study(course, factory):
    return factory.study(course=course)


@pytest.mark.parametrize(
    ("id", "length"),
    [
        ("1", 1),
        ("2", 0),
    ],
)
@pytest.mark.usefixtures("study")
def test_ok(as_superuser, id, length):
    response = as_superuser.get(f"/api/v2/users/?course={id}")

    assert len(response) == length
