from core.conf.environ import env

VAT_ID = env("VAT_ID", cast=str, default=None)
COMPANY_NAME = env("COMPANY_NAME", cast=str, default=None)
SIGNATURE_PATH = env("SIGNATURE_PATH", cast=str, default="/dev/null")
