import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def _set_frontend_url(settings):
    settings.FRONTEND_URL = "https://education.borshev.com/lms/"


@pytest.fixture
def question(mixer):
    return mixer.blend("homework.Question", slug="068e2b1a-613b-4924-be6b-7b3d0c4dedb7")


def test(question):
    assert question.get_absolute_url() == "https://education.borshev.com/lms/homework/question-admin/068e2b1a-613b-4924-be6b-7b3d0c4dedb7/"
