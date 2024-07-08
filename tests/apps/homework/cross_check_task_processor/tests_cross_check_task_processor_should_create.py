import pytest

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def mocked_source_cross_check(mocker, crosscheck):
    return mocker.patch(
        "apps.homework.services.cross_check_task_processor.CrossCheckTaskProcessor.source_cross_check",
        new_callable=mocker.PropertyMock,
        return_value=crosscheck,
    )


@pytest.fixture(autouse=True)
def mocked_required_cross_check(mocker, crosscheck):
    return mocker.patch(
        "apps.homework.services.cross_check_task_processor.CrossCheckTaskProcessor.required_cross_check",
        new_callable=mocker.PropertyMock,
        return_value=crosscheck,
    )


@pytest.fixture
def processor(processor, answer):
    return processor(answer)


def test_should_not_create_when_source_cross_check_is_none(processor, mocked_source_cross_check):
    mocked_source_cross_check.return_value = None

    assert not processor.should_create()


def test_should_not_create_when_required_cross_check_is_none(processor, mocked_required_cross_check):
    mocked_required_cross_check.return_value = None

    assert not processor.should_create()


def test_should_create_when_source_cross_check_and_required_cross_check_are_not_none(processor):
    assert processor.should_create()
