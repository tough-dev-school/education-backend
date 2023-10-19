import pytest

from apps.chains.models import Progress

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time("2032-12-01 15:30"),
]


@pytest.fixture
def another_chain(mixer):
    return mixer.blend("chains.Chain")


def test_no_progress(study, chain):
    assert Progress.objects.get_last_progress(chain, study) is None


def test_single_progress(chain, study, mixer, progress):
    assert Progress.objects.get_last_progress(chain, study) == progress


@pytest.mark.usefixtures("progress")
def test_same_chain_is_used(another_chain, study, mixer, progress):
    assert Progress.objects.get_last_progress(another_chain, study) is None


def test_latest_progress_is_used(mixer, freezer, chain, study, progress, message):
    freezer.move_to("2032-12-01 16:30")

    latest_progress = mixer.blend("chains.Progress", message=message, study=study)

    assert Progress.objects.get_last_progress(chain, study) == latest_progress
