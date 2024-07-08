import pytest

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def ya_answer_on_ya_answer(mixer, question, ya_answer, user):
    return mixer.blend("homework.Answer", question=question, parent=ya_answer, author=user)


@pytest.fixture
def crosscheck_task(mixer, answer_on_ya_answer, crosscheck, ya_crosscheck):
    return mixer.blend("homework.CrossCheckTask", answer=answer_on_ya_answer, source_cross_check=crosscheck, required_cross_check=ya_crosscheck)


def test_returns_none_without_crosschecks(processor, answer):
    processor = processor(answer)

    assert processor.required_cross_check is None


@pytest.mark.usefixtures("crosscheck")
def test_returns_available_crosscheck(processor, answer_on_ya_answer, ya_crosscheck):
    processor = processor(answer_on_ya_answer)

    assert processor.required_cross_check == ya_crosscheck


@pytest.mark.usefixtures("ya_answer_on_answer", "ya_crosscheck", "crosscheck")
def test_returns_none_if_last_crosscheck_is_checked(processor, answer_on_ya_answer):
    processor = processor(answer_on_ya_answer)

    assert processor.required_cross_check is None


def test_returns_none_if_last_crosscheck_is_in_tasks(processor, answer_on_ya_answer, ya_crosscheck, mixer):
    mixer.blend("homework.CrossCheckTask", source_cross_check=ya_crosscheck)

    processor = processor(answer_on_ya_answer)

    assert processor.required_cross_check is None


@pytest.mark.usefixtures("crosscheck_task")
def test_returns_same_crosscheck_for_answer_from_same_author(processor, ya_crosscheck, ya_answer_on_ya_answer):
    processor = processor(ya_answer_on_ya_answer)

    assert processor.required_cross_check == ya_crosscheck
