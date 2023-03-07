import pytest

pytestmark = [pytest.mark.django_db]


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("/test/create", "https://api.dashamail.com/test/create"),
        ("test/create", "https://api.dashamail.com/test/create"),
        ("test/create/?par=val", "https://api.dashamail.com/test/create/?par=val"),
        (
            "test/create/?par=val&par1=val1",
            "https://api.dashamail.com/test/create/?par=val&par1=val1",
        ),
    ],
)
def test_format_url(url, expected, dashamail):
    assert dashamail.http.format_url(url) == expected
