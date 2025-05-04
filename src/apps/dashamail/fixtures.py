import pytest


@pytest.fixture(autouse=True)
def _enable_dashamail(request, settings):
    if request.node.get_closest_marker("dashamail") is not None:
        settings.DASHAMAIL_API_KEY = "testDashamailAPIKey100500"
