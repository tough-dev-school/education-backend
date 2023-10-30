from core.conf.environ import env

AMOCRM_BASE_URL = env("AMOCRM_BASE_URL", cast=str, default="")
AMOCRM_REDIRECT_URL = env("AMOCRM_REDIRECT_URL", cast=str, default="")
AMOCRM_INTEGRATION_ID = env("AMOCRM_INTEGRATION_ID", cast=str, default="")
AMOCRM_CLIENT_SECRET = env("AMOCRM_CLIENT_SECRET", cast=str, default="")
AMOCRM_AUTHORIZATION_CODE = env("AMOCRM_AUTHORIZATION_CODE", cast=str, default="")
AMOCRM_B2C_PIPELINE_NAME = env("AMOCRM_B2C_PIPELINE_NAME", cast=str, default="b2c")
