import pytest

pytestmark = [pytest.mark.django_db]


@pytest.mark.parametrize(
    "field",
    [
        "name",
        "slug",
    ],
)
def test_retrieve(api, record, field):
    got = api.get(f"/api/v2/records/{record.slug}/")

    assert got[field] == getattr(record, field)
