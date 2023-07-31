from app.conf.environ import env

AMOCRM_BASE_URL = env("AMOCRM_BASE_URL", cast=str, default="")
AMOCRM_INTEGRATION_ID = env("AMOCRM_INTEGRATION_ID", cast=str, default="")
AMOCRM_CLIENT_SECRET = env("AMOCRM_CLIENT_SECRET", cast=str, default="")
