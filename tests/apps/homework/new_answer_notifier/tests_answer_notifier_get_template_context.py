import pytest

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
def parent_of_answer(mixer, question, answer):
    return mixer.blend("homework.Answer", question=question, author=answer.author, parent=answer)


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


@pytest.fixture
def crosscheck(mixer, answer, another_answer):
    return mixer.blend("homework.AnswerCrossCheck", checker=answer.author, answer=another_answer)


@pytest.fixture(autouse=True)
def _freeze_absolute_url(settings):
    settings.FRONTEND_URL = "https://frontend/lms/"


def test_default(notifier, answer, user):
    notifier = notifier(answer)
    assert notifier.get_notification_context(user) == dict(
        discussion_url="https://frontend/lms/homework/answers/f593d1a9-120c-4c92-bed0-9f037537d4f4/",
        discussion_name="Вторая домашка",
        answer_text="<p>Сарынь на кичку!</p>",
        author_name="Петрович Львов",
        is_non_root_answer_author="1",
        without_not_checked_crosschecks="1",
    )


def test_root_answer(notifier, answer, another_answer):
    answer.update(parent=another_answer)

    context = notifier(answer).get_notification_context(answer.author)

    assert (
        context["discussion_url"] == "https://frontend/lms/homework/answers/16a973e4-40f1-4887-a502-beeb5677ab42/#f593d1a9-120c-4c92-bed0-9f037537d4f4"
    ), "Should be the link to the first answer with anchor to the current"


def test_markdown_to_html(notifier, answer):
    answer.update(text="# Вил би хтмл хедер")

    context = notifier(answer).get_notification_context(answer.author)

    assert context["answer_text"] == "<h1>Вил би хтмл хедер</h1>"


def test_is_root_answer_author_flag(notifier, answer):
    context = notifier(answer).get_notification_context(answer.author)

    assert context["is_root_answer_author"] == "1"


def test_img_removed(notifier, answer):
    answer.update(
        text="Hello, you![Top 23 Great Job Memes for a Job Well Done That You'll Want to Share | Great  job meme, Job memes, Good job quotes](https://i.pinimg.com/736x/13/ff/49/13ff49773ca9c25ac2116c8bc6c4d2ee.jpg)"
    )

    text = notifier(answer).get_text_with_markdown()

    assert text == "<p>Hello, you</p>"


@pytest.mark.usefixtures("crosscheck")
def test_with_not_checked_crosscheck(notifier, parent_of_answer, answer):
    context = notifier(parent_of_answer).get_notification_context(answer.author)

    assert context["crosschecks"][0]["crosscheck_url"] == "https://frontend/lms/homework/answers/16a973e4-40f1-4887-a502-beeb5677ab42/"
    assert context["crosschecks"][0]["crosscheck_author_name"] == "Василич Теркин"


def test_when_crosscheck_is_checked(notifier, crosscheck, parent_of_answer, answer):
    crosscheck.checked_at = "2022-10-09 10:30:12+12:00"
    crosscheck.save()

    context = notifier(parent_of_answer).get_notification_context(answer.author)

    assert context["without_not_checked_crosschecks"] == "1"
    assert "crosschecks" not in context


@pytest.mark.usefixtures("crosscheck")
def test_crosscheck_when_comment_to_comment(notifier, parent_of_answer, answer, mixer):
    parent = mixer.blend("homework.Answer", question=answer.question, parent=parent_of_answer)

    context = notifier(parent).get_notification_context(answer.author)

    assert context["without_not_checked_crosschecks"] == "1"
    assert "crosschecks" not in context


@pytest.mark.usefixtures("crosscheck")
def test_crosscheck_when_someone_add_comment_to_my_comment_on_another_answer(notifier, another_answer, answer, mixer):
    parent = mixer.blend("homework.Answer", question=answer.question, parent=another_answer, author=answer.author)
    my_answer = mixer.blend("homework.Answer", question=answer.question, parent=parent)

    context = notifier(my_answer).get_notification_context(answer.author)

    assert context["without_not_checked_crosschecks"] == "1"
    assert "crosschecks" not in context


@pytest.mark.usefixtures("crosscheck")
def test_crosscheck_when_answer_from_another_question(notifier, parent_of_answer, answer, mixer):
    parent_of_answer.question = mixer.blend("homework.Question")
    parent_of_answer.save()

    context = notifier(parent_of_answer).get_notification_context(answer.author)

    assert context["without_not_checked_crosschecks"] == "1"
    assert "crosschecks" not in context
