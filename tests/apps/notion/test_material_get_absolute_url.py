import pytest

pytestmark = [pytest.mark.django_db]


def test(mixer, settings):
    settings.FRONTEND_URL = "https://frontend.url/lms/"
    material = mixer.blend("notion.Material", slug="4d5726e8-ee52-4448-b8f9-7be4c7f8e632")

    assert material.get_absolute_url() == "https://frontend.url/lms/materials/4d5726e8ee524448b8f97be4c7f8e632/"
