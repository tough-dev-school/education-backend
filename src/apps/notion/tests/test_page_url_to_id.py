import pytest

from apps.notion.helpers import page_url_to_id


@pytest.mark.parametrize(
    ("page_url", "expected"),
    [
        ("https://notion.so/workspace/100500ddf", "100500ddf"),
        ("https://notion.so/workspace/100500ddf/", "100500ddf"),
        ("https://notion.so/workspace/100500ddf/?v=test", "100500ddf"),
        ("https://notion.so/workspace/100500ddf?v=test", "100500ddf"),
        ("100500ddf", "100500ddf"),
        ("https://notion.so/workspace/a-b-c-100500ddf", "100500ddf"),
    ],
)
def test(page_url, expected):
    assert page_url_to_id(page_url) == expected
