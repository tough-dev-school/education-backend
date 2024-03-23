import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def _set_frontend_url(settings):
    settings.FRONTEND_URL = "https://education.borshev.com/lms/"


ROOT_ANSWER_SLUG = "16623c2d-1b35-4586-b62b-3a6308c58d71"
FIRST_CHILD_SLUG = "8971c40a-a5fd-4f80-8146-d711f7790239"
SECOND_CHILD_SLUG = "68ce5fc1-a5bb-420a-b48c-8769f0434784"


@pytest.fixture
def answer(mixer):
    return mixer.blend("homework.Answer", slug=ROOT_ANSWER_SLUG)


def test_root(answer):
    assert answer.get_absolute_url() == f"https://education.borshev.com/lms/homework/answers/{ROOT_ANSWER_SLUG}/"


def test_first_level_child(answer, mixer):
    first_level_child = mixer.blend("homework.Answer", parent=answer, slug=FIRST_CHILD_SLUG)

    assert first_level_child.get_absolute_url() == f"https://education.borshev.com/lms/homework/answers/{ROOT_ANSWER_SLUG}/#{FIRST_CHILD_SLUG}"


def test_second_level_child(answer, mixer):
    first_level_child = mixer.blend("homework.Answer", parent=answer)
    second_level_child = mixer.blend("homework.Answer", parent=first_level_child, slug=SECOND_CHILD_SLUG)

    assert second_level_child.get_absolute_url() == f"https://education.borshev.com/lms/homework/answers/{ROOT_ANSWER_SLUG}/#{SECOND_CHILD_SLUG}"
