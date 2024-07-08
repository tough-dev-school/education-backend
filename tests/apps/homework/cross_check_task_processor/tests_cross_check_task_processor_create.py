from unittest.mock import PropertyMock

import pytest

from apps.homework.services.cross_check_task_processor import CrossCheckTaskProcessor

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def mocked_source_cross_check(mocker, crosscheck):
    return mocker.patch.object(CrossCheckTaskProcessor, "source_cross_check", new_callable=PropertyMock, return_value=crosscheck)


@pytest.fixture(autouse=True)
def mocked_required_cross_check(mocker, ya_crosscheck):
    return mocker.patch.object(CrossCheckTaskProcessor, "required_cross_check", new_callable=PropertyMock, return_value=ya_crosscheck)


def test_create(processor, answer, crosscheck, ya_crosscheck):
    processor = processor(answer)

    got = processor.create()

    assert got.answer == answer
    assert got.source_cross_check == crosscheck
    assert got.required_cross_check == ya_crosscheck
