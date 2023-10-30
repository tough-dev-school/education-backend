from core.conf.environ import env

EMAIL_ENABLED = env("EMAIL_ENABLED", cast=bool, default=False)

EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")

DASHAMAIL_API_KEY = env("DASHAMAIL_API_KEY", default="")
DASHAMAIL_LIST_ID = env("DASHAMAIL_LIST_ID", default="")

DEFAULT_FROM_EMAIL = env("EMAIL_FROM", cast=str, default="")
DEFAULT_REPLY_TO = env("REPLY_TO", cast=str, default=DEFAULT_FROM_EMAIL)

ANYMAIL = {
    "POSTMARK_SERVER_TOKEN": env("POSTMARK_SERVER_TOKEN", cast=str, default=""),
    "DEBUG_API_REQUESTS": env("DEBUG"),
}

RECEIPTS_EMAIL = env("RECEIPTS_EMAIL", cast=str, default="receipts@tough-dev.school")
DANGEROUS_OPERATION_HAPPENED_EMAILS = env(
    "DANGEROUS_OPERATION_HAPPENED_EMAILS",
    cast=tuple,
    default=["fedor@borshev.com", "marianaonysko@gmail.com"],
)

# Postmark template IDs
PASSWORDLESS_TOKEN_TEMPLATE_ID = env("PASSWORDLESS_TOKEN_TEMPLATE_ID", cast=str, default="passwordless-token")
PASSWORD_RESET_TEMPLATE_ID = env("PASSWORD_RESET_TEMPLATE_ID", cast=str, default="password-reset")
