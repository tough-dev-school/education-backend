import pytest

from apps.chains.models import Chain

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def get_editable():
    return lambda: Chain.objects.editable()


@pytest.fixture
def chain(mixer):
    return mixer.blend("chains.Chain", sending_is_active=False, archived=False)


def test_include_active_not_archived_chains(get_editable, chain):
    got = get_editable()

    assert chain in got


def test_exclude_sending_is_active_chains(get_editable, chain):
    chain.update(sending_is_active=True)

    got = get_editable()

    assert chain not in got


def test_exclude_archived_chains(get_editable, chain):
    chain.update(archived=True)

    got = get_editable()

    assert chain not in got
