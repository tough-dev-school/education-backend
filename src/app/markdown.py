import bleach
import cmarkgfm
from django.conf import settings


def markdownify(content):
    html = cmarkgfm.github_flavored_markdown_to_html(content)

    return bleach.clean(
        text=html,
        tags=settings.BLEACH_ALLOWED_TAGS,
        attributes=settings.BLEACH_ALLOWED_ATTRIBUTES,
        strip_comments=False,
    )
