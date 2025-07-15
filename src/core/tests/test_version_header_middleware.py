import pytest

pytestmark = [pytest.mark.django_db]


def test_adds_version_header_for_localhost(api):
    response = api.get("/", HTTP_HOST="localhost", as_response=True)

    assert "debug=False" in response["X-Backend-Version"]
    assert "CI-testing" in response["X-Backend-Version"]


def test_does_not_add_version_header_for_other_hosts(api):
    """Test that the middleware doesn't add the X-Version header for non-localhost hosts"""
    response = api.get("/", HTTP_HOST="example.com", as_response=True)

    assert "X-Version" not in response
