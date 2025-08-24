from functools import partial

import pytest

from apps.b2b.services import DealCompleter


@pytest.fixture
def completer(deal):
    return partial(DealCompleter, deal=deal)


@pytest.fixture
def seller(mixer):
    return mixer.blend("users.User")
