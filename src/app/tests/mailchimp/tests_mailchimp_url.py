import pytest

pytestmark = [pytest.mark.django_db]


@pytest.mark.parametrize(
    'url, expected',
    [
        ['/test/create', 'https://us05.api.mailchimp.com/3.0/test/create'],
        ['test/create', 'https://us05.api.mailchimp.com/3.0/test/create'],
        ['test/create/?par=val', 'https://us05.api.mailchimp.com/3.0/test/create/?par=val'],
        [
            'test/create/?par=val&par1=val1',
            'https://us05.api.mailchimp.com/3.0/test/create/?par=val&par1=val1',
        ],
    ],
)
def test_format_url(url, expected, mailchimp):
    assert mailchimp.http.format_url(url) == expected
