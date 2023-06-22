import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def _enable_homework_permissions_checking(settings):
    settings.DISABLE_HOMEWORK_PERMISSIONS_CHECKING = False


@pytest.fixture
def question(mixer):
    return mixer.blend("homework.Question", name="Вторая домашка")


@pytest.fixture
def answer(mixer, question):
    return mixer.blend("homework.Answer", question=question)
