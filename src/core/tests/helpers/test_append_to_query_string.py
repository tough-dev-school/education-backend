import pytest

from core.helpers import append_to_query_string


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (
            {"lol": "kek", "url": "https://tst.hst/"},
            "https://tst.hst/?lol=kek",
        ),
        (
            {"lol": "kek", "url": "https://tst.hst/?lol1=kek1"},
            "https://tst.hst/?lol1=kek1&lol=kek",
        ),
        (
            {"lol": "kek", "url": "https://tst.hst/?kek=lol"},
            "https://tst.hst/?kek=lol&lol=kek",
        ),
        (
            {"lol": "kek", "lol3": "kek3", "url": "https://tst.hst/?kek=lol"},
            "https://tst.hst/?kek=lol&lol=kek&lol3=kek3",
        ),
    ],
)
def test(data, expected):
    assert append_to_query_string(**data) == expected
