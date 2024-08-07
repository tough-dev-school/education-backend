import pytest

from apps.homework.models import AnswerCrossCheck

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def question(mixer):
    return mixer.blend("homework.Question")


@pytest.fixture
def ya_question(mixer):
    return mixer.blend("homework.Question")


@pytest.fixture
def crosscheck(mixer, question):
    return mixer.blend("homework.AnswerCrossCheck", answer__question=question)


@pytest.fixture
def ya_crosscheck(mixer, question):
    return mixer.blend("homework.AnswerCrossCheck", answer__question=question)


@pytest.mark.usefixtures("crosscheck", "ya_crosscheck")
def test_without_checked(question):
    got = AnswerCrossCheck.objects.count_for_question(question)

    assert got["checked"] == 0
    assert got["total"] == 2


@pytest.mark.usefixtures("ya_crosscheck")
def test_with_checked(crosscheck, question):
    crosscheck.checked_at = "2022-01-01 00:00:00Z"
    crosscheck.save()

    got = AnswerCrossCheck.objects.count_for_question(question)

    assert got["checked"] == 1
    assert got["total"] == 2


@pytest.mark.usefixtures("crosscheck", "ya_crosscheck")
def test_for_ya_question(ya_question):
    got = AnswerCrossCheck.objects.count_for_question(ya_question)

    assert got["checked"] == 0
    assert got["total"] == 0
