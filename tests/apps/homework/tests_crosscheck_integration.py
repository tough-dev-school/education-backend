import pytest

from apps.homework import tasks
from apps.homework.models import AnswerCrossCheck

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def questions(mixer, course):
    questions = mixer.cycle(2).blend("homework.Question")
    course.question_set.add(*questions)
    return questions


@pytest.fixture
def users(mixer):
    return mixer.cycle(10).blend("users.User")


@pytest.fixture(autouse=True)
def _allow_course_access(factory, users, course):
    for user in users:
        order = factory.order(user=user)
        order.set_item(course)
        order.set_paid()


@pytest.fixture(autouse=True)
def _allow_email_sending(settings):
    settings.EMAIL_ENABLED = True


@pytest.fixture
def submit_answer(api):
    def _submit(author, answer, question):
        api.auth(author)
        api.post(
            "/api/v2/homework/answers/",
            {
                "question": question.slug,
                **answer,
            },
        )

    return _submit


@pytest.fixture
def submit_homework(users, submit_answer, mailoutbox):
    def _submit(question):
        for user in users:
            submit_answer(
                author=user,
                question=question,
                answer={
                    "text": f"Горите в аду. С любовью, {user}",
                },
            )

    return _submit


def test_single_homework(users, submit_homework, questions, mailoutbox):
    submit_homework(questions[0])
    tasks.disptach_crosscheck(questions[0].id)

    assert len(mailoutbox) == 10

    for user in users:
        assert AnswerCrossCheck.objects.filter(checker=user).count() == 3


def test_triple_homework(users, submit_homework, questions, mailoutbox):
    for _ in range(3):
        submit_homework(questions[0])

    tasks.disptach_crosscheck(questions[0].id)

    assert len(mailoutbox) == 10
    for user in users:
        assert AnswerCrossCheck.objects.filter(checker=user).count() == 3
