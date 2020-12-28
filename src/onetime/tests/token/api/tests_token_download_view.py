import pytest
import uuid

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time('2032-12-01 15:30'),
]


def test_ok(api, token, get_url):
    api.get(f'/api/v2/download/{token.token}/', expected_status_code=302)

    get_url.assert_called_once()


def test_404_for_bad_uuid(api, token):
    fake_uuid = str(uuid.uuid4())  # may fail once in a century, sorry

    api.get(f'/api/v2/download/{fake_uuid}/', expected_status_code=404)


def test_404_for_expires_token(api, token):
    token.setattr_and_save('expires', '2030-01-01')

    api.get(f'/api/v2/download/{token.token}/', expected_status_code=404)
