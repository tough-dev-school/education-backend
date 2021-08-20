from bleach.sanitizer import ALLOWED_ATTRIBUTES as _ALLOWED_ATTRIBUTES
from bleach.sanitizer import ALLOWED_TAGS as _ALLOWED_TAGS

MARKDOWNX_URLS_PATH = '/api/v2/markdownx/markdownify/'
MARKDOWNX_UPLOAD_URLS_PATH = '/api/v2/markdownx/upload/'
MARKDOWNX_MARKDOWNIFY_FUNCTION = 'app.markdown.markdownify'

BLEACH_ALLOWED_TAGS = [
    *_ALLOWED_TAGS,
    'p',
    'img',
    'br',
    'hr',
    'pre',
    'h1',
    'h2',
    'h3',
    'h4',
    'h5',
    'h3',
]

BLEACH_ALLOWED_ATTRIBUTES = {
    **_ALLOWED_ATTRIBUTES,
    'img': {
        'src',
        'alt',
    },
}
