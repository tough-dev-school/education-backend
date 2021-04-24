import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def _set_frontend_url(settings):
    settings.FRONTEND_URL = 'https://education.borshev.com/lms/'


@pytest.fixture
def question(mixer):
    return mixer.blend('homework.Question', slug='068e2b1a-613b-4924-be6b-7b3d0c4dedb7')


@pytest.fixture
def answer(question, mixer):
    return mixer.blend('homework.Answer', question=question, slug='16623c2d-1b35-4586-b62b-3a6308c58d71')


def test(answer):
    assert answer.get_absolute_url() == 'https://education.borshev.com/lms/homework/questions/068e2b1a-613b-4924-be6b-7b3d0c4dedb7/#16623c2d-1b35-4586-b62b-3a6308c58d71'
