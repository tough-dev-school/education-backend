import pytest

from apps.notion.rewrite import rewrite_links


@pytest.fixture(autouse=True)
def rewrite_mapping(mocker):
    return mocker.patch(
        "apps.notion.rewrite.links.get_link_rewrite_mapping",
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

def rewrite(block):
    return rewrite_links(block)["value"]["properties"]


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

    result = rewrite(block)

    assert result[prop_name] == [
        "Пыщ-Пыщ",
        [
            [
                "a",
                "/a4a1c6f6d2ea441ebf1fdd8b5b99445a",
            ],
        ],
    ]


@pytest.mark.parametrize("prop_name", ["title", "caption"])
def test_title_is_rewritten_with_get_params(block, prop_name):
    block["value"]["properties"][prop_name] = [
        "Пыщ-Пыщ",
        [
            [
                "a",
                "/their-material-id?good=to-go",
            ],
        ],
    ]

    result = rewrite(block)

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

    result = rewrite_links(block)["value"]["properties"]["title"]

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


@pytest.mark.parametrize("link", ["https://text.com", "https://text.com?good=to-go"])
def test_external_links_are_not_rewritten(block, link):
    block["value"]["properties"]["title"] = [
        "Пыщ-Пыщ",
        [
            [
                "a",
                link,
            ],
        ],
    ]

    result = rewrite(block)

    assert result["title"] == [
        "Пыщ-Пыщ",
        [
            [
                "a",
                link,
            ],
        ],
    ]

@pytest.mark.parametrize("link", ["/id-not-in-mapping", "/id-not-in-mapping?good=to-go"])
def test_links_not_from_mapping_are_not_rewritten(block, link):
    block["value"]["properties"]["title"] = [
        "Пыщ-Пыщ",
        [
            [
                "a",
                link,
            ],
        ],
    ]

    result = rewrite(block)

    assert result["title"] == [
        "Пыщ-Пыщ",
        [
            [
                "a",
                link,
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

    result = rewrite(block)

    assert result["title"] == weird_text
