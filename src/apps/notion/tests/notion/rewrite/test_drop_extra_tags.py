import pytest

from apps.notion.rewrite import drop_extra_tags


@pytest.fixture
def block():
    return {
        "role": "reader",
        "value": {
            "format": {
                "page_icon": "1.ico",
                "random_key": "random_value",
            },
            "second_level_value_to_drop": "test",
            "second_level_key_to_drop": {
                "test": "__expired",
            },
            "parent_id": "will_no_be_dropped",
        },
    }


def test_extra_tags_are_dropped(block):
    block = drop_extra_tags(block)

    assert "role" not in block
    assert "second_level_value_to_drop" not in block
    assert "second_level_key_to_drop" not in block


def test_required_values_are_not_dropped(block):
    block = drop_extra_tags(block)

    assert block["value"]["parent_id"] == "will_no_be_dropped"
    assert block["value"]["format"]["page_icon"] == "1.ico"
    assert block["value"]["format"]["random_key"] == "random_value"  # wildcards work wll
