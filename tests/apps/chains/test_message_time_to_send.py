import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time("2032-12-01 15:30:00"),
]


@pytest.mark.usefixtures("progress")
def test_time_has_not_passed(message, study):
    assert message.time_to_send(study=study) is False


def test_time_has_not_passed_if_there_is_no_progress(message, study, progress, freezer):
    freezer.move_to("2032-12-01 15:35:00")

    progress.delete()

    assert message.time_to_send(study=study) is False


def test_time_has_not_passed_for_root_messages(message, study, progress, freezer):
    progress.delete()
    message.update(parent=None)

    freezer.move_to("2032-12-01 15:35:00")

    assert message.time_to_send(study=study) is False


@pytest.mark.usefixtures("progress")
def test_time_has_passed(message, freezer, study):
    freezer.move_to("2032-12-01 15:35:00")

    assert message.time_to_send(study=study) is True
