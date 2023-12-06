import pytest


@pytest.fixture(autouse=True)
def _pause_dashamail(mocker, request):
    """Pause dashamail background jobs"""
    if request.node.get_closest_marker("dashamail") is None:
        mocker.patch("apps.dashamail.lists.client.DashamailListsClient.subscribe_or_update")

@pytest.fixture(autouse=True)
def _pause_flags(mocker, request):
    """Pause background flags rebuilding"""
    if request.node.get_closest_marker("user_tags_rebuild") is None:
        mocker.patch("apps.users.tasks.generate_tags")
