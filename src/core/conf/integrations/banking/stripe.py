import stripe

from core.conf.environ import env

STRIPE_USD_API_KEY = env("STRIPE_USD_API_KEY", cast=str, default="")
STRIPE_USD_WEBHOOK_SECRET = env("STRIPE_USD_WEBHOOK_SECRET", cast=str, default="")

STRIPE_KZT_API_KEY = env("STRIPE_KZT_API_KEY", cast=str, default="")
STRIPE_KZT_WEBHOOK_SECRET = env("STRIPE_KZT_WEBHOOK_SECRET", cast=str, default="")

stripe.enable_telemetry = False
