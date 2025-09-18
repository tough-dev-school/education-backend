from core.prosemirror import prosemirror_to_text


def doc(content: list[dict]) -> dict:
    return {
        "type": "doc",
        "content": content,
    }


def text(text: str, **kwargs) -> dict:
    return {
        "type": "text",
        "text": text,
        **kwargs,
    }


def test_two_paragraphs_and_a_heading():
    assert (
        prosemirror_to_text(
            doc(
                [
                    {"type": "heading", "content": [text("Заголовок")]},
                    {"type": "paragraph", "content": [text("Раз")]},
                    {"type": "paragraph", "content": [text("Два", marks={"type": "bold"})]},
                ]
            )
        )
        == "Заголовок\n\nРаз\n\nДва"
    )


def test_hard_break():
    assert (
        prosemirror_to_text(
            doc(
                [
                    {"type": "paragraph", "content": [text("Раз")]},
                    {"type": "hardBreak"},
                    {"type": "paragraph", "content": [text("Два")]},
                ]
            )
        )
        == "Раз\n\nДва"
    )


def test_list():
    assert (
        prosemirror_to_text(
            doc(
                [
                    {"type": "paragraph", "content": [text("Раз")]},
                    {
                        "type": "orderedList",
                        "attrs": {"type": None, "start": 1},
                        "content": [
                            {
                                "type": "listItem",
                                "content": [
                                    {"type": "paragraph", "content": [{"text": "list-text-1", "type": "text"}]},
                                    {"type": "paragraph", "content": [{"text": "list-text-2", "type": "text"}]},
                                ],
                            }
                        ],
                    },
                    {"type": "paragraph", "content": [text("Два")]},
                ]
            )
        )
        == "Раз\n\nДва"
    )
