import pytest

from apps.notion.rewrite import rewrite


@pytest.fixture(autouse=True)
def rewrite_mapping(mocker):
    return mocker.patch(
        "apps.notion.rewrite.get_rewrite_mapping",
        return_value={
            "their-material-id": "a4a1c6f6d2ea441ebf1fdd8b5b99445a",
        },
    )


@pytest.fixture
def block():
    return {
        "value": {
            "properties": {},
        },
    }


@pytest.mark.parametrize("prop_name", ["title", "caption"])
def test_title_is_rewritten(block, prop_name):
    block["value"]["properties"][prop_name] = [
        "Пыщ-Пыщ",
        [
            [
                "a",
                "/their-material-id",
            ],
        ],
    ]

    result = rewrite(block)["value"]["properties"]

    assert result[prop_name] == [
        "Пыщ-Пыщ",
        [
            [
                "a",
                "/a4a1c6f6d2ea441ebf1fdd8b5b99445a",
            ],
        ],
    ]


def test_recursivity(block):
    block["value"]["properties"]["title"] = [
        "Пыщ-Пыщ",
        [
            [
                [
                    "stuff",
                    [  # NOQA: JS101
                        [
                            "a",
                            "/their-material-id",
                        ],
                    ],
                ]
            ]
        ],  # NOQA: JS102
    ]  # NOQA: JS102

    result = rewrite(block)["value"]["properties"]["title"]

    assert result == [
        "Пыщ-Пыщ",
        [
            [
                [
                    "stuff",
                    [  # NOQA: JS101
                        [
                            "a",
                            "/a4a1c6f6d2ea441ebf1fdd8b5b99445a",
                        ],
                    ],
                ]
            ]
        ],  # NOQA: JS102
    ]  # NOQA: JS102
    ...


def test_external_links_are_not_rewritten(block):
    block["value"]["properties"]["title"] = [
        "Пыщ-Пыщ",
        [
            [
                "a",
                "https://test.com",
            ],
        ],
    ]

    result = rewrite(block)["value"]["properties"]

    assert result["title"] == [
        "Пыщ-Пыщ",
        [
            [
                "a",
                "https://test.com",
            ],
        ],
    ]


def test_links_not_from_mapping(block):
    block["value"]["properties"]["title"] = [
        "Пыщ-Пыщ",
        [
            [
                "a",
                "/id-not-in-mapping",
            ],
        ],
    ]

    result = rewrite(block)["value"]["properties"]

    assert result["title"] == [
        "Пыщ-Пыщ",
        [
            [
                "a",
                "/id-not-in-mapping",
            ],
        ],
    ]


@pytest.mark.parametrize(
    "weird_text",
    [
        [
            ["a", [["'b'"]]],
            ["uthorized.", [["'i'"], ["'b'"]]],
            [
                " weird text",
            ],
        ],
    ],
)
def test_weird_text(block, weird_text):
    block["value"]["properties"]["title"] = weird_text

    result = rewrite(block)["value"]["properties"]

    assert result["title"] == weird_text
