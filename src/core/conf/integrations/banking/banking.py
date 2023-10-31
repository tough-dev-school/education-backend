from core.conf.environ import env

BANKS_REFUNDS_ENABLED = env("BANKS_REFUNDS_ENABLED", cast=bool, default=not env("DEBUG"))  # by default the opposite to DEBUG
