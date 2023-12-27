import pytest


@pytest.fixture(autouse=True)
def _pause_auditlog(mocker, request):
    if request.node.get_closest_marker("auditlog") is None:
        mocker.patch("core.tasks.write_admin_log.write_admin_log.delay")

        mocker.patch("apps.orders.services.order_paid_setter.OrderPaidSetter.write_success_admin_log")
        mocker.patch("apps.orders.services.order_refunder.OrderRefunder.write_success_admin_log")


@pytest.fixture(autouse=True)
def _pause_dashamail(mocker, request):
    """Pause dashamail background jobs"""
    if request.node.get_closest_marker("dashamail") is None:
        mocker.patch("apps.dashamail.tasks.update_subscription.delay")
        mocker.patch("apps.dashamail.tasks.update_subscription.apply_async")

        mocker.patch("apps.dashamail.tasks.push_order_event.delay")
        mocker.patch("apps.dashamail.tasks.push_order_event.si")
        mocker.patch("apps.dashamail.tasks.push_order_event.apply_async")

        mocker.patch("apps.dashamail.tasks.directcrm_subscribe.delay")
        mocker.patch("apps.dashamail.tasks.directcrm_subscribe.si")
        mocker.patch("apps.dashamail.tasks.directcrm_subscribe.apply_async")

@pytest.fixture(autouse=True)
def _pause_tags(mocker, request):
    """Pause background flags rebuilding"""
    if request.node.get_closest_marker("user_tags_rebuild") is None:
        mocker.patch("apps.users.tasks.rebuild_tags.delay")
        mocker.patch("apps.users.tasks.rebuild_tags.apply_async")
        mocker.patch("apps.users.tasks.generate_tags")
