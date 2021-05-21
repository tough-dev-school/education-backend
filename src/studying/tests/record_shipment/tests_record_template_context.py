import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def url(mocker):
    return mocker.patch('app.integrations.s3.AppS3.get_presigned_url', return_value='https://downloa.d/home.video.mp4')


def test_template_context(shipment):
    ctx = shipment.get_template_context()

    assert ctx['name_genitive'] == 'Кройки и шитья'
    assert ctx['record_link'] == 'https://downloa.d/home.video.mp4'
