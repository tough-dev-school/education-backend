import pytest

from core.helpers import is_valid_uuid


@pytest.mark.parametrize(
    ("input", "expected"),
    [
        ("a2d45300-401d-4f85-a9af-71bf12a9876c", True),
        ("00000000-0000-0000-0000-000000000000", True),  # nil UUID
        ("not-a-uuid", False),
        ("12345", False),
        ("a2d45300-401d-4f85-a9af-12345", False),  # incomplete UUID
        (None, False),
    ],
)
def test_is_valid_uuid(input, expected):
    assert is_valid_uuid(input) == expected
