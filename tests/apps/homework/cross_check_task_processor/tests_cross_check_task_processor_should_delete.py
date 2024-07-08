import pytest

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def crosscheck_task(mixer, crosscheck, ya_crosscheck):
    return mixer.blend("homework.CrossCheckTask", source_cross_check=crosscheck, required_cross_check=ya_crosscheck)


@pytest.fixture
def ya_crosscheck_task(mixer, crosscheck, ya_crosscheck):
    return mixer.blend("homework.CrossCheckTask", source_cross_check=ya_crosscheck, required_cross_check=crosscheck)


def test_should_not_delete_if_no_tasks(processor, answer):
    processor = processor(answer)

    assert processor.should_delete() is False


@pytest.mark.usefixtures("crosscheck", "ya_crosscheck", "ya_crosscheck_task")
def test_should_delete_if_required_cross_check_exist(processor, answer_on_ya_answer):
    processor = processor(answer_on_ya_answer)

    assert processor.should_delete() is True


@pytest.mark.usefixtures("crosscheck", "ya_crosscheck", "crosscheck_task")
def test_should_delete_if_requires_cross_check_exist_for_another_task(processor, ya_answer_on_answer):
    processor = processor(ya_answer_on_answer)

    assert processor.should_delete() is True


@pytest.mark.usefixtures("crosscheck", "ya_crosscheck", "ya_crosscheck_task")
def test_should_not_delete_task_with_source_cross_check(processor, ya_answer_on_answer):
    processor = processor(ya_answer_on_answer)

    assert processor.should_delete() is False
