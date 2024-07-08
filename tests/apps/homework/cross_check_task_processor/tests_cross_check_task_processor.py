import pytest

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def mocked_should_create(mocker):
    return mocker.patch("apps.homework.services.cross_check_task_processor.CrossCheckTaskProcessor.should_create", return_value=False)


@pytest.fixture(autouse=True)
def mocked_should_delete(mocker):
    return mocker.patch("apps.homework.services.cross_check_task_processor.CrossCheckTaskProcessor.should_delete", return_value=False)


@pytest.fixture(autouse=True)
def mocked_create(mocker):
    return mocker.patch("apps.homework.services.cross_check_task_processor.CrossCheckTaskProcessor.create")


@pytest.fixture(autouse=True)
def mocked_delete(mocker):
    return mocker.patch("apps.homework.services.cross_check_task_processor.CrossCheckTaskProcessor.delete")


@pytest.mark.parametrize(
    ("should_create", "expected"),
    [
        (True, True),
        (False, False),
    ],
)
def test_calls_create(processor, answer, mocked_should_create, mocked_create, should_create, expected):
    mocked_should_create.return_value = should_create

    processor(answer)()

    assert mocked_create.called is expected


@pytest.mark.parametrize(
    ("should_delete", "expected"),
    [
        (True, True),
        (False, False),
    ],
)
def test_calls_delete(processor, answer, mocked_should_delete, mocked_delete, should_delete, expected):
    mocked_should_delete.return_value = should_delete

    processor(answer)()

    assert mocked_delete.called is expected
