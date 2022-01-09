import pytest

pytestmark = [pytest.mark.django_db]


def test(mixer, settings):
    settings.FRONTEND_URL = 'https://frontend.url/lms/'
    material = mixer.blend('notion.Material', page_id='100500ddf')

    assert material.get_absolute_url() == 'https://frontend.url/lms/materials/100500ddf/'
