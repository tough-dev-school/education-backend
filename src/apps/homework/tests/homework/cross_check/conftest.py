import pytest

from apps.homework.services import AnswerCrossCheckDispatcher, QuestionCrossCheckDispatcher

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def admin(factory):
    return factory.user()


@pytest.fixture
def module(factory, course):
    return factory.module(course=course)


@pytest.fixture
def another_module(factory, another_course):
    return factory.module(course=another_course)


@pytest.fixture
def lesson(factory, module):
    return factory.lesson(module=module)


@pytest.fixture
def another_lesson(factory, another_module):
    return factory.lesson(module=another_module)


@pytest.fixture
def question(factory, lesson):
    question = factory.question()

    lesson.update(question=question)

    return question


@pytest.fixture
def another_question(factory, another_lesson):
    question = factory.question()

    another_lesson.update(question=question)

    return question


@pytest.fixture(autouse=True)
def answers(mixer, question, user, another_user):
    return [
        mixer.blend("homework.Answer", question=question, author=user, parent=None),
        mixer.blend("homework.Answer", question=question, author=another_user, parent=None),
    ]


@pytest.fixture
def answers_to_another_question(mixer, another_question):
    even_more_users = mixer.cycle(2).blend("users.User")
    return [
        mixer.blend("homework.Answer", question=another_question, author=even_more_users[0], parent=None),
        mixer.blend("homework.Answer", question=another_question, author=even_more_users[1], parent=None),
    ]


@pytest.fixture
def answer_dispatcher(admin):
    def _dispatcher(**kwargs):
        return AnswerCrossCheckDispatcher(author=admin, **kwargs)

    return _dispatcher


@pytest.fixture
def question_dispatcher(question, admin):
    return QuestionCrossCheckDispatcher(question=question, author=admin, answers_per_user=1)
