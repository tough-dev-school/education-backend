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
def another_answer(mixer, question):
    return mixer.blend(
        "homework.Answer",
        question=question,
        slug="16a973e4-40f1-4887-a502-beeb5677ab42",
        text="Банзай!",
    )


@pytest.fixture(autouse=True)
def _freeze_absolute_url(settings):
    settings.FRONTEND_URL = "https://frontend/lms/"


def test_default(notifier, answer, user):
    notifier = notifier(answer)
    assert notifier.get_notification_context(user) == dict(
        discussion_url="https://frontend/lms/homework/answers/f593d1a9-120c-4c92-bed0-9f037537d4f4/",
        discussion_name="Вторая домашка",
        answer_title="Сарынь на кичку!",
        author_name="Петрович Львов",
        is_non_root_answer_author="1",
    )


def test_root_answer(notifier, answer, another_answer):
    answer.update(parent=another_answer)

    context = notifier(answer).get_notification_context(answer.author)

    assert (
        context["discussion_url"] == "https://frontend/lms/homework/answers/16a973e4-40f1-4887-a502-beeb5677ab42/#f593d1a9-120c-4c92-bed0-9f037537d4f4"
    ), "Should be the link to the first answer with anchor to the current"


def test_html_is_stripped(notifier, answer):
    answer.update(text="# Россия вперёд!")

    context = notifier(answer).get_notification_context(answer.author)

    assert context["answer_title"] == "Россия вперёд!"


def test_is_root_answer_author_flag(notifier, answer):
    context = notifier(answer).get_notification_context(answer.author)

    assert context["is_root_answer_author"] == "1"
