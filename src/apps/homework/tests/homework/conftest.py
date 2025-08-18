import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def question(mixer):
    return mixer.blend("homework.Question", name="Вторая домашка")


@pytest.fixture
def answer(mixer, question):
    return mixer.blend("homework.Answer", question=question)


@pytest.fixture
def comments(answer, mixer, another_user):
    return mixer.cycle(2).blend("homework.Answer", parent=answer, question=answer.question, author=another_user)


@pytest.fixture
def crosscheck_that_user_should_perform(mixer, answer):
    return mixer.blend(
        "homework.AnswerCrossCheck",
        checker=answer.author,
        answer=mixer.blend("homework.Answer", question=answer.question),
        checked=None,
    )


@pytest.fixture
def one_more_crosscheck_that_user_should_perform(mixer, answer):
    return mixer.blend(
        "homework.AnswerCrossCheck",
        checker=answer.author,
        answer=mixer.blend("homework.Answer", question=answer.question),
        checked=None,
    )


@pytest.fixture
def crosscheck_that_user_should_recieve(mixer, answer, another_user):
    return mixer.blend(
        "homework.AnswerCrossCheck",
        checker=another_user,
        answer=answer,
        checked=None,
    )


@pytest.fixture
def crosschecks(crosscheck_that_user_should_recieve, crosscheck_that_user_should_perform):
    return {
        "recieved": crosscheck_that_user_should_recieve,
        "to_perform": crosscheck_that_user_should_perform,
    }
