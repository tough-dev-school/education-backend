import bleach
from bleach.sanitizer import ALLOWED_ATTRIBUTES, ALLOWED_TAGS
from markdown import markdown
from markdownx.settings import MARKDOWNX_MARKDOWN_EXTENSION_CONFIGS, MARKDOWNX_MARKDOWN_EXTENSIONS


def markdownify(content):
    html = markdown(
        text=content,
        extensions=MARKDOWNX_MARKDOWN_EXTENSIONS,
        extension_configs=MARKDOWNX_MARKDOWN_EXTENSION_CONFIGS,
        output_format='html5',
    )

    return bleach.clean(
        text=html,
        tags=[
            *ALLOWED_TAGS,
            'p',
            'img',
        ],
        attributes={
            **ALLOWED_ATTRIBUTES,
            'img': {
                'src',
            },
        },
    )
