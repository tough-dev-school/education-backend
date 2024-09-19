import pytest

from apps.notion.models import Video
from apps.notion.rewrite import rewrite_youtube_links

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def block():
    return {
        "value": {
            "properties": {},
        },
    }


@pytest.fixture(autouse=True)
def _video_mapping():
    Video.objects.create(
        youtube_id="dVo80vW4ekw",
        rutube_id="c30a209fe2e31c0d1513b746e168b1a3",
    )


def rewrite(block):
    return rewrite_youtube_links(block)["value"]["properties"]


@pytest.mark.parametrize("prop_name", ["title", "caption"])
def youtube_links_are_rewritten(block, prop_name):
    block["value"]["properties"][prop_name] = [
        "Пыщ-Пыщ",
        [
            [
                "a",
                "https://www.youtube.com/watch?v=dVo80vW4ekw",
            ],
        ],
    ]

    result = rewrite(block)

    assert result[prop_name] == [
        "Пыщ-Пыщ",
        [
            [
                "a",
                "https://rutube.ru/video/c30a209fe2e31c0d1513b746e168b1a3/",
            ],
        ],
    ]


def test_recursion(block):
    block["value"]["properties"]["title"] = [
        "Пыщ-Пыщ",
        [
            [
                "stuff",
                [
                    [
                        "a",
                        "https://www.youtube.com/watch?v=dVo80vW4ekw",
                    ]
                ],
            ],
        ],
    ]

    result = rewrite(block)

    assert result["title"] == [
        "Пыщ-Пыщ",
        [
            [
                "stuff",
                [
                    [
                        "a",
                        "https://rutube.ru/video/c30a209fe2e31c0d1513b746e168b1a3/",
                    ]
                ],
            ],
        ],
    ]


def test_non_youtube_link_is_not_rewritten(block):
    block["value"]["properties"]["title"] = [
        "Пыщ-Пыщ",
        [
            [
                "a",
                "https://text.com",
            ],
        ],
    ]

    result = rewrite(block)

    assert result["title"] == [
        "Пыщ-Пыщ",
        [
            [
                "a",
                "https://text.com",
            ],
        ],
    ]


def test_youtube_short_link_is_rewritten(block):
    block["value"]["properties"]["title"] = [
        "Пыщ-Пыщ",
        [
            [
                "a",
                "https://youtu.be/dVo80vW4ekw",
            ],
        ],
    ]

    result = rewrite(block)

    assert result["title"] == [
        "Пыщ-Пыщ",
        [
            [
                "a",
                "https://rutube.ru/video/c30a209fe2e31c0d1513b746e168b1a3/",
            ],
        ],
    ]


def test_links_without_matching_video_are_not_rewritten(block):
    Video.objects.all().delete()

    block["value"]["properties"]["title"] = [
        "Пыщ-Пыщ",
        [
            [
                "a",
                "https://www.youtube.com/watch?v=dVo80vW4ekw",
            ],
        ],
    ]

    result = rewrite(block)

    assert result["title"] == [
        "Пыщ-Пыщ",
        [
            [
                "a",
                "https://www.youtube.com/watch?v=dVo80vW4ekw",
            ],
        ],
    ]
