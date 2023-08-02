import pytest

from amocrm import tasks

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def mock_course_creator(mocker):
    mocker.patch("amocrm.services.course_creator.AmoCRMCourseCreator.__call__")
    return mocker.patch("amocrm.services.course_creator.AmoCRMCourseCreator.__init__", return_value=None)


@pytest.fixture
def mock_course_updater(mocker):
    mocker.patch("amocrm.services.course_updater.AmoCRMCourseUpdater.__call__")
    return mocker.patch("amocrm.services.course_updater.AmoCRMCourseUpdater.__init__", return_value=None)


def test_call_course_creator_if_not_amocrm_course(course, mock_course_creator, mock_course_updater):
    tasks.push_course(course_id=course.id)

    mock_course_creator.assert_called_once_with(course=course)
    mock_course_updater.assert_not_called()


def test_call_course_updater_if_amocrm_course_exists(amocrm_course, mock_course_creator, mock_course_updater):
    tasks.push_course(course_id=amocrm_course.course.id)

    mock_course_updater.assert_called_once_with(amocrm_course=amocrm_course)
    mock_course_creator.assert_not_called()
