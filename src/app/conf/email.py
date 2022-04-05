from app.conf.environ import env

EMAIL_ENABLED = env('EMAIL_ENABLED', cast=bool, default=False)

EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')

DASHAMAIL_API_KEY = env('DASHAMAIL_API_KEY', default='3f151d7fef15b61312d1c334e296c90f')
DASHAMAIL_LIST_ID = env('DASHAMAIL_LIST_ID', default='79357')

DEFAULT_FROM_EMAIL = env('EMAIL_FROM', cast=str, default='')
ANYMAIL = {
    'POSTMARK_SERVER_TOKEN': env('POSTMARK_SERVER_TOKEN', cast=str, default=''),
    'DEBUG_API_REQUESTS': env('DEBUG'),
}
