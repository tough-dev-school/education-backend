import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def get_url(mocker):
    return mocker.patch("app.integrations.s3.AppS3.get_presigned_url", return_value="https://test.com")


@pytest.fixture
def record(mixer):
    return mixer.blend("products.Record", s3_object_id="homevideo-2032-12-01.mp4")


def test_works(record):
    url = record.get_url()

    assert url == "https://test.com"


def test_s3_is_called_with_correct_signature(record, get_url):
    record.get_url(expires=138)

    get_url.assert_called_once_with("homevideo-2032-12-01.mp4", expires=138)
