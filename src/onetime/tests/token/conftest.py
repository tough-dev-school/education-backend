import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def get_url(mocker):
    return mocker.patch('app.s3.AppS3.get_presigned_url', return_value='https://test.com')


@pytest.fixture
def record(mixer):
    return mixer.blend('courses.Record', s3_object_id='homevideo-2032-12-01.mp4')


@pytest.fixture
def token(mixer, record):
    return mixer.blend('onetime.Token', record=record)


def test_url_is_correct(token):
    assert token.download() == 'https://test.com'
