from core.conf.environ import env

SENTRY_DSN = env("SENTRY_DSN", cast=str, default="")

if not env("DEBUG") and SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.httpx import HttpxIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    def strip_transactions(event, hint):  # type: ignore[no-untyped-def]
        del hint

        if event["transaction"] in (
            "/api/v2/healthchecks/{service}/",
            "apps.chains.tasks.send_chain_messages",
            "apps.chains.tasks.send_active_chains",
            "/admin/jsi18n/",
        ):
            return None

        return event

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration(), CeleryIntegration(), RedisIntegration(), HttpxIntegration()],
        traces_sample_rate=0.8,
        send_default_pii=True,
        before_send_transaction=strip_transactions,
    )
