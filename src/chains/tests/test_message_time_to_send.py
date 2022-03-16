import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time('2032-12-01 15:30:00'),
]


@pytest.fixture
def chain(mixer):
    return mixer.blend('chains.Chain')


@pytest.fixture
def parent_message(mixer):
    return mixer.blend('chains.Message', parent=None)


@pytest.fixture(autouse=True)
def progress(parent_message, mixer, study):
    return mixer.blend('chains.Progress', message=parent_message, study=study)


@pytest.fixture
def message(mixer, parent_message):
    return mixer.blend('chains.Message', parent=parent_message, delay=3)


def test_time_has_not_passed(message, study):
    assert message.time_to_send(to=study) is False


def test_time_has_not_passed_if_there_is_no_progress(message, study, progress, freezer):
    freezer.move_to('2032-12-01 15:35:00')

    progress.delete()

    assert message.time_to_send(to=study) is False


def test_time_has_not_passed_for_root_messages(message, study, progress, freezer):
    progress.delete()
    message.setattr_and_save('parent', None)

    freezer.move_to('2032-12-01 15:35:00')

    assert message.time_to_send(to=study) is False


def test_time_has_passed(message, freezer, study):
    freezer.move_to('2032-12-01 15:35:00')

    assert message.time_to_send(to=study) is True
