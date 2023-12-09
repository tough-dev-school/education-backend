import pytest

from apps.dashamail.directcrm.frontend import DashamailFrontendHTTP


@pytest.fixture
def http(respx_mock):
    http = DashamailFrontendHTTP()
    http.respx_mock = respx_mock

    return http


def test_format_payload(http):
    payload = {
        "originDomain": "testdomain.com",
        "deviceUUID": "d2bd8523-ea50-4dc1-a0b4-2f88462c6e20",
        "ianaTimeZone": "Europe/Moscow",
        "operation": "ViewProduct",
        "data": {
            "product": {
                "productId": "test-course-slug",
            },
        }
    }

    assert http.format_payload(payload) == "originDomain=testdomain.com&deviceUUID=d2bd8523-ea50-4dc1-a0b4-2f88462c6e20&operation=ViewProduct&ianaTimeZone=Europe%2FMoscow&data=%7B%22product%22%3A+%7B%22productId%22%3A+%22test-course-slug%22%7D%7D"
