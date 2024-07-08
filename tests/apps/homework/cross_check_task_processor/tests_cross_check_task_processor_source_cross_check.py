import pytest

pytestmark = [
    pytest.mark.django_db,
]


@pytest.mark.usefixtures("crosscheck")
def test_without_related_crosscheck(answer, processor):
    processor = processor(answer)

    assert processor.source_cross_check is None


def test_with_related_crosscheck(answer_on_ya_answer, crosscheck, processor):
    processor = processor(answer_on_ya_answer)

    assert processor.source_cross_check == crosscheck


def test_another_related_crosscheck(ya_answer_on_answer, ya_crosscheck, processor):
    processor = processor(ya_answer_on_answer)

    assert processor.source_cross_check == ya_crosscheck
