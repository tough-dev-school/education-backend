import pytest

from apps.notion.helpers import id_to_uuid


@pytest.mark.parametrize(
    ("input", "expected"),
    [
        ("5b71111b97365bb88577b7765b00a05a", "5b71111b-9736-5bb8-8577-b7765b00a05a"),
        ("5b71111b-9736-5bb8-8577-b7765b00a05a", "5b71111b-9736-5bb8-8577-b7765b00a05a"),
    ],
)
def test(input, expected):
    assert id_to_uuid(input) == expected
