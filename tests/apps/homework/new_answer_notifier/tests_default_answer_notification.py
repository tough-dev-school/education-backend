import pytest

from apps.homework.services.new_answer_notifier import DefaultAnswerNotification

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def answer(mixer, question):
    return mixer.blend(
        "homework.Answer",
        question=question,
        slug="f593d1a9-120c-4c92-bed0-9f037537d4f4",
        text="Сарынь на кичку!",
        author__first_name="Петрович",
        author__last_name="Львов",
    )


@pytest.fixture
def another_answer(mixer, question):
    return mixer.blend(
        "homework.Answer",
        question=question,
        slug="16a973e4-40f1-4887-a502-beeb5677ab42",
        text="Банзай!",
        author__first_name="Василич",
        author__last_name="Теркин",
    )


@pytest.fixture(autouse=True)
def _freeze_absolute_url(settings):
    settings.FRONTEND_URL = "https://frontend/lms/"


@pytest.fixture
def notification():
    return DefaultAnswerNotification


def test_template_id(notification, answer):
    assert notification(answer=answer, user=answer.author).get_template_id() == "new-answer-notification"


def test_should_send(notification, answer):
    assert notification(answer=answer, user=answer.author).should_send() is True


def test_default(notification, answer, user):
    notification = notification(answer=answer, user=user)

    assert notification.get_context() == dict(
        discussion_url="https://frontend/lms/homework/answers/f593d1a9-120c-4c92-bed0-9f037537d4f4/",
        discussion_name="Вторая домашка",
        answer_text="<p>Сарынь на кичку!</p>",
        author_name="Петрович Львов",
        is_non_root_answer_author="1",
    )


def test_root_answer(notification, answer, another_answer):
    answer.update(parent=another_answer)

    context = notification(answer=answer, user=answer.author).get_context()

    assert (
        context["discussion_url"] == "https://frontend/lms/homework/answers/16a973e4-40f1-4887-a502-beeb5677ab42/#f593d1a9-120c-4c92-bed0-9f037537d4f4"
    ), "Should be the link to the first answer with anchor to the current"


def test_markdown_to_html(notification, answer):
    answer.update(text="# Вил би хтмл хедер")

    context = notification(answer=answer, user=answer.author).get_context()

    assert context["answer_text"] == "<h1>Вил би хтмл хедер</h1>"


def test_is_root_answer_author_flag(notification, answer):
    context = notification(answer=answer, user=answer.author).get_context()

    assert context["is_root_answer_author"] == "1"


def test_img_removed(notification, answer):
    answer.update(
        text="Hello, you![Top 23 Great Job Memes for a Job Well Done That You'll Want to Share | Great  job meme, Job memes, Good job quotes](https://i.pinimg.com/736x/13/ff/49/13ff49773ca9c25ac2116c8bc6c4d2ee.jpg)"
    )

    text = notification(answer=answer, user=answer.author).get_text_with_markdown()

    assert text == "<p>Hello, you</p>"


def test_send(notification, send_mail, answer, user):
    notification(answer=answer, user=user).send()

    send_mail.assert_called_once_with(
        to=user.email,
        template_id="new-answer-notification",
        ctx={
            "discussion_name": "Вторая домашка",
            "discussion_url": "https://frontend/lms/homework/answers/f593d1a9-120c-4c92-bed0-9f037537d4f4/",
            "answer_text": "<p>Сарынь на кичку!</p>",
            "author_name": "Петрович Львов",
            "is_non_root_answer_author": "1",
        },
        disable_antispam=True,
    )


@pytest.mark.parametrize("should_send", [True, False])
def test_send_if_should(notification, answer, mocker, should_send):
    mocker.patch("apps.homework.services.new_answer_notifier.DefaultAnswerNotification.should_send", return_value=should_send)
    mocked_send = mocker.patch("apps.homework.services.new_answer_notifier.DefaultAnswerNotification.send")

    got = notification(answer=answer, user=answer.author).send_if_should()

    assert got is should_send
    assert mocked_send.called is should_send
