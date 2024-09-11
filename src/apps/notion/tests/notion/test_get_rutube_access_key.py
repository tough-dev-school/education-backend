import pytest

from apps.notion.helpers import get_rutube_access_key


@pytest.mark.parametrize(
    "input, expected",
    [
        ("https://rutube.ru/video/dc26809c58022f1a1f4acfe3b86297a4/", None),
        ("https://rutube.ru/video/dc26809c58022f1a1f4acfe3b86297a4/?p=10K7TJntZwspv8QViYHMwg", "10K7TJntZwspv8QViYHMwg"),
        ("https://rutube.ru/video/dc26809c58022f1a1f4acfe3b86297a4/?p=10K7TJntZwspv8QViYHMwg&utm=22pv8QViYHMwg10K7TJntZ", "10K7TJntZwspv8QViYHMwg"),
        ("https://rutube.ru/video/dc26809c58022f1a1f4acfe3b86297a4/?k=10K7TJntZwspv8QViYHMwg", None),
        ("dc26809c58022f1a1f4acfe3b86297a4", None),
        ("https://youtu.be/1aSDLtmircA", None),
        ("https://s3-us-west-2.amazonaws.com/secure.notion-static.com/9294be93-51f7-4b61-b330-cdf098234a34/diagrams.mp4", None),
    ],
)
def test(input, expected):
    assert get_rutube_access_key(input) == expected
