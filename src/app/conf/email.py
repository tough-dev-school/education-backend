from app.conf.environ import env

EMAIL_ENABLED = env('EMAIL_ENABLED', cast=bool, default=False)

EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')

MAILCHIMP_API_KEY = env('MAILCHIMP_API_KEY', default='')
MAILCHIMP_CONTACT_LIST_ID = env('MAILCHIMP_CONTACT_LIST_ID', cast=str, default=None)

DEFAULT_FROM_EMAIL = env('EMAIL_FROM', cast=str, default='')
ANYMAIL = {
    'POSTMARK_SERVER_TOKEN': env('POSTMARK_SERVER_TOKEN', cast=str, default=''),
    'DEBUG_API_REQUESTS': env('DEBUG'),
}
