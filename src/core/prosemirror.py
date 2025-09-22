class ProseMirrorException(ValueError): ...


def _extract_text(node: dict) -> str:
    """Recursively extract text from a ProseMirror node."""
    if node["type"] == "text":
        return node["text"]

    text_parts = []
    for child_node in node.get("content", []):
        text_parts.append(_extract_text(child_node))

    return "".join(text_parts).strip()


def prosemirror_to_text(data: dict) -> str:
    """Convert ProseMirror document to plain text with paragraph separation."""
    if data.get("type") != "doc":
        raise ProseMirrorException("Not a prosemirror document")

    paragraphs = [_extract_text(node) for node in data["content"] if node["type"] in ["heading", "paragraph"]]

    return "\n\n".join(paragraphs)
