from core.conf.environ import env

DASHAMAIL_API_KEY = env("DASHAMAIL_API_KEY", default="")
DASHAMAIL_LIST_ID = env("DASHAMAIL_LIST_ID", default="")

DASHAMAIL_DIRECTCRM_ENDPOINT = env("DASHAMAIL_DIRECTCRM_ENDPOINT", default="")
DASHAMAIL_DIRECTCRM_SECRET_KEY = env("DASHAMAIL_DIRECTCRM_SECRET_KEY", default="")