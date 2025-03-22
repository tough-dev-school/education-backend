from apps.notion.types import BlockId, TextProperty


def get_links(node: TextProperty) -> list[BlockId]:
    """Recursively find links in the notion block content"""
    links = []
    for child in node:
        if not isinstance(child, list):  # ignore plain text
            continue

        if all(isinstance(i, str) for i in child):  # each list of strings may be a link
            if len(child) >= 1 and child[0] == "a" and isinstance(child[1], str) and child[1].startswith("/"):  # it is a link, and the link is internal
                link = child[1]

                if '#' in link:
                    link = link.split("#")[0]  # remove anchors

                if '?' in link:
                    link = link.split("?")[0]  # remove GET params

                link = link.replace("/", "")  # remove first slash

                links.append(link)
        else:  # iterate over all child nodes
            for grand_child in child:
                links += get_links(grand_child)

    return links


__all__ = ["get_links"]
