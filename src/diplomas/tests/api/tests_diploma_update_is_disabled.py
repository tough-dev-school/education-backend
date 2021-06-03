import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def api(api):
    api.user.is_superuser = True
    api.user.save()

    return api


def test(api, factory, diploma):
    api.put(f'/api/v2/diplomas/{diploma.slug}/', {
        'image': factory.uploaded_image(),
    }, format='multipart', expected_status_code=405)
