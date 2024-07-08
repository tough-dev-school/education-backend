import pytest

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def crosscheck_task(mixer, answer_on_ya_answer, crosscheck, ya_crosscheck):
    return mixer.blend("homework.CrossCheckTask", answer=answer_on_ya_answer, source_cross_check=crosscheck, required_cross_check=ya_crosscheck)


@pytest.fixture
def ya_crosscheck_task(mixer, ya_answer_on_answer, crosscheck, ya_crosscheck):
    return mixer.blend("homework.CrossCheckTask", answer=ya_answer_on_answer, source_cross_check=ya_crosscheck, required_cross_check=crosscheck)


def test_delete_crosscheck_task(processor, answer_on_ya_answer, crosscheck_task, ya_crosscheck_task):
    processor = processor(answer_on_ya_answer)

    processor.delete()

    with pytest.raises(crosscheck_task.DoesNotExist):
        ya_crosscheck_task.refresh_from_db()

    crosscheck_task.refresh_from_db()  # doesnt raise


def test_delete_another_crosscheck_task(processor, ya_answer_on_answer, crosscheck_task, ya_crosscheck_task):
    processor = processor(ya_answer_on_answer)

    processor.delete()

    with pytest.raises(crosscheck_task.DoesNotExist):
        crosscheck_task.refresh_from_db()

    ya_crosscheck_task.refresh_from_db()  # doesnt raise
