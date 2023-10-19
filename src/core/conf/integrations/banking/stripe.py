from core.conf.environ import env

STRIPE_API_KEY = env("STRIPE_API_KEY", cast=str, default="")
STRIPE_WEBHOOK_SECRET = env("STRIPE_WEBHOOK_SECRET", cast=str, default="")
