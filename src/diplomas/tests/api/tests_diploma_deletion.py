import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def api(api):
    api.user.is_superuser = True
    api.user.save()

    return api


def test(api, diploma):
    api.delete(f'/api/v2/diplomas/{diploma.slug}/', expected_status_code=405)
