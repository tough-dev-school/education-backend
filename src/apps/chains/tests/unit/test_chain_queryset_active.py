import pytest

from apps.chains.models import Chain

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def get_active():
    return lambda: Chain.objects.active()


def test_include_chains(get_active, chain) -> None:
    got = get_active()

    assert chain in got


def test_exclude_sending_is_active_turned_off(get_active, chain) -> None:
    chain.update(sending_is_active=False)

    got = get_active()

    assert chain not in got


def test_exclude_archived_chains(get_active, chain) -> None:
    chain.update(archived=True)

    got = get_active()

    assert chain not in got
