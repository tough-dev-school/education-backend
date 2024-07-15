import pytest

from apps.homework.services.new_answer_notifier import CrossCheckedAnswerNotification

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def _freeze_absolute_url(settings):
    settings.FRONTEND_URL = "https://frontend/lms/"


@pytest.fixture
def ya_question(mixer):
    return mixer.blend("homework.Question")


@pytest.fixture
def notification():
    return CrossCheckedAnswerNotification


@pytest.fixture
def answer(mixer, question):
    return mixer.blend(
        "homework.Answer",
        question=question,
        slug="f593d1a9-120c-4c92-bed0-9f037537d4f4",
        author__first_name="Петрович",
        author__last_name="Львов",
    )


@pytest.fixture
def ya_answer(mixer, question):
    return mixer.blend(
        "homework.Answer",
        question=question,
        slug="f593d1a9-120c-4c92-bed0-9f037537d4f2",
        author__first_name="Василиса",
        author__last_name="Прекрасная",
    )


@pytest.fixture
def child_answer(mixer, answer, question):
    return mixer.blend(
        "homework.Answer",
        question=question,
        parent=answer,
        slug="16a973e4-40f1-4887-a502-beeb5677ab42",
        author__first_name="Василич",
        author__last_name="Теркин",
    )


@pytest.fixture
def comment_on_child_answer(mixer, question, child_answer):
    return mixer.blend(
        "homework.Answer",
        question=question,
        parent=child_answer,
    )


@pytest.fixture
def crosscheck(mixer, ya_answer, answer):
    return mixer.blend("homework.AnswerCrossCheck", answer=ya_answer, checker=answer.author)


def test_template_id(notification, answer):
    assert notification(answer=answer, user=answer.author).get_template_id() == "crosschecked-answer-notification"


@pytest.mark.usefixtures("crosscheck")
def test_can_be_sent(notification, answer, child_answer):
    assert notification(answer=child_answer, user=answer.author).can_be_sent() is True


@pytest.mark.usefixtures("crosscheck")
def test_cannot_be_sent_when_user_is_not_root_answer_author(notification, child_answer, ya_answer):
    assert notification(answer=child_answer, user=ya_answer.author).can_be_sent() is False


@pytest.mark.usefixtures("crosscheck")
def test_cannot_be_sent_if_answer_is_root(notification, answer):
    assert notification(answer=answer, user=answer.author).can_be_sent() is False


def test_cannot_be_sent_if_answer_is_a_comment_to_child_answer(notification, answer, comment_on_child_answer):
    assert notification(answer=comment_on_child_answer, user=answer.author).can_be_sent() is False


def test_cannot_be_sent_if_theres_no_non_completed_crosscheck(notification, answer, child_answer, crosscheck):
    crosscheck.checked_at = "2021-01-01 00:00:00Z"
    crosscheck.save()

    assert notification(answer=child_answer, user=answer.author).can_be_sent() is False


def test_cannot_be_sent_if_crosscheck_belongs_to_another_question(notification, crosscheck, answer, child_answer, ya_question):
    crosscheck.answer.question = ya_question
    crosscheck.answer.save()

    assert notification(answer=child_answer, user=answer.author).can_be_sent() is False


@pytest.mark.usefixtures("crosscheck")
def test_context(notification, answer, child_answer):
    context = notification(answer=child_answer, user=answer.author).get_context()

    assert context == {
        "discussion_name": "Вторая домашка",
        "discussion_url": "https://frontend/lms/homework/answers/f593d1a9-120c-4c92-bed0-9f037537d4f4/#16a973e4-40f1-4887-a502-beeb5677ab42",
        "author_name": "Василич Теркин",
        "crosschecks": [
            {
                "crosscheck_url": "https://frontend/lms/homework/answers/f593d1a9-120c-4c92-bed0-9f037537d4f2/",
                "crosscheck_author_name": "Василиса Прекрасная",
            }
        ],
    }
