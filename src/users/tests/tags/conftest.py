import pytest

from django.utils import timezone


@pytest.fixture
def user(user):
    user.tags = []
    user.save()
    return user


@pytest.fixture
def paid_order(factory, user):
    return factory.order(user=user, paid=timezone.now(), unpaid=None, shipped=None)


@pytest.fixture
def unpaid_order(factory, user):
    return factory.order(user=user, unpaid=timezone.now(), paid=None, shipped=None)


@pytest.fixture(autouse=True)
def mock_subscribe_to_dashamail(mocker):
    return mocker.patch("users.tags.pipeline.subscribe_user_to_dashamail")
