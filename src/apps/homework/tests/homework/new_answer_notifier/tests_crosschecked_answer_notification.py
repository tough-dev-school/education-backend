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
def test_should_send(notification, answer, child_answer):
    assert notification(answer=child_answer, user=answer.author).should_send() is True


@pytest.mark.usefixtures("crosscheck")
def test_cannot_be_sent_when_user_is_not_root_answer_author(notification, child_answer, ya_answer):
    assert notification(answer=child_answer, user=ya_answer.author).should_send() is False


@pytest.mark.usefixtures("crosscheck")
def test_cannot_be_sent_if_answer_is_root(notification, answer):
    assert notification(answer=answer, user=answer.author).should_send() is False


def test_cannot_be_sent_if_answer_is_a_comment_to_child_answer(notification, answer, comment_on_child_answer):
    assert notification(answer=comment_on_child_answer, user=answer.author).should_send() is False


def test_cannot_be_sent_if_theres_no_non_completed_crosscheck(notification, answer, child_answer, crosscheck):
    crosscheck.checked_at = "2021-01-01 00:00:00Z"
    crosscheck.save()

    assert notification(answer=child_answer, user=answer.author).should_send() is False


def test_cannot_be_sent_if_crosscheck_belongs_to_another_question(notification, crosscheck, answer, child_answer, ya_question):
    crosscheck.answer.question = ya_question
    crosscheck.answer.save()

    assert notification(answer=child_answer, user=answer.author).should_send() is False


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


@pytest.mark.usefixtures("crosscheck")
def test_send(notification, answer, child_answer, send_mail):
    notification(answer=child_answer, user=answer.author).send()

    send_mail.assert_called_once_with(
        to=answer.author.email,
        template_id="crosschecked-answer-notification",
        ctx={
            "discussion_name": "Вторая домашка",
            "discussion_url": "https://frontend/lms/homework/answers/f593d1a9-120c-4c92-bed0-9f037537d4f4/#16a973e4-40f1-4887-a502-beeb5677ab42",
            "author_name": "Василич Теркин",
            "crosschecks": [
                {
                    "crosscheck_url": "https://frontend/lms/homework/answers/f593d1a9-120c-4c92-bed0-9f037537d4f2/",
                    "crosscheck_author_name": "Василиса Прекрасная",
                }
            ],
        },
        disable_antispam=True,
    )


@pytest.mark.parametrize("should_send", [True, False])
def test_send_if_should(notification, answer, mocker, should_send):
    mocker.patch("apps.homework.services.new_answer_notifier.CrossCheckedAnswerNotification.should_send", return_value=should_send)
    mocked_send = mocker.patch("apps.homework.services.new_answer_notifier.CrossCheckedAnswerNotification.send")

    got = notification(answer=answer, user=answer.author).send_if_should()

    assert got is should_send
    assert mocked_send.called is should_send
