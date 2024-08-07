import pytest

from core.helpers import lower_first


@pytest.mark.parametrize(
    ("input", "expected"),
    [
        ("a", "a"),
        ("ХУЙ", "хУЙ"),
        ("Камаз Навоза", "камаз Навоза"),
    ],
)
def test(input, expected):
    assert lower_first(input) == expected
