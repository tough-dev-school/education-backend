from core.conf.environ import env

BOT_TOKEN = env("BOT_TOKEN", cast=str, default=None)
HAPPINESS_MESSAGES_CHAT_ID = env("HAPPINESS_MESSAGES_CHAT_ID", cast=str, default=None)
