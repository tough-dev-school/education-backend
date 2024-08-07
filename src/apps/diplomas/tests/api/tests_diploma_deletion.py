import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def api(api):
    api.user.update(is_superuser=True)

    return api


def test(api, diploma):
    api.delete(f"/api/v2/diplomas/{diploma.slug}/", expected_status_code=405)
