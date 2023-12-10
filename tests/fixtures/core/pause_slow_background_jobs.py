import pytest


@pytest.fixture(autouse=True)
def _pause_dashamail(mocker, request):
    """Pause dashamail background jobs"""
    if request.node.get_closest_marker("dashamail") is None:
        mocker.patch("apps.dashamail.tasks.update_subscription.delay")
        mocker.patch("apps.dashamail.tasks.update_subscription.apply_async")
        mocker.patch("apps.dashamail.lists.client.DashamailListsClient.subscribe_or_update")

@pytest.fixture(autouse=True)
def _pause_tags(mocker, request):
    """Pause background flags rebuilding"""
    if request.node.get_closest_marker("user_tags_rebuild") is None:
        mocker.patch("apps.users.tasks.rebuild_tags.delay")
        mocker.patch("apps.users.tasks.rebuild_tags.apply_async")
        mocker.patch("apps.users.tasks.generate_tags")
