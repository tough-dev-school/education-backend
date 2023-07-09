import pytest

pytestmark = [pytest.mark.django_db]


@pytest.mark.parametrize(
    "field",
    [
        "name",
        "slug",
    ],
)
def test_retrieve(api, course, field):
    got = api.get(f"/api/v2/courses/{course.slug}/")

    assert got[field] == getattr(course, field)
