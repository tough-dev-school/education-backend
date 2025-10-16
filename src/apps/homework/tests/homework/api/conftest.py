import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def api(api):
    """We test it as normal student, not superuser to check permissions"""
    api.user.update(is_superuser=False)

    return api


@pytest.fixture
def question(factory, course):
    """Question that belongs to a course"""
    question = factory.question(name="Пятнадцатая домашка")

    factory.lesson(
        module=factory.module(course=course),
        question=question,
    )

    return question


@pytest.fixture
def another_question(factory, course):
    question = factory.question(name="Шестнадцатая домашка")

    factory.lesson(
        module=factory.module(course=course),
        question=question,
    )

    return question


@pytest.fixture
def another_course(mixer, course, another_course):
    """Let another course be in the same group as the original course courses in the suite be in the same group"""
    group = mixer.blend("products.Group")

    course.update(group=group)
    another_course.update(group=group)

    return another_course


@pytest.fixture
def question_of_another_course(factory, another_course):
    """The name is intenationaly the same as the 'question' fixture"""
    question = factory.question(name="Пятнадцатая домашка")

    factory.lesson(
        module=factory.module(course=another_course),
        question=question,
    )

    return question


@pytest.fixture
def answer(mixer, question, api):
    return mixer.blend(
        "homework.Answer",
        question=question,
        author=api.user,
        content={"type": "doc", "text": "Пыщ!"},
    )


@pytest.fixture
def another_answer(mixer, question, api):
    return mixer.blend("homework.Answer", question=question, author=api.user)


@pytest.fixture
def child_answer(answer, mixer):
    return mixer.blend("homework.Answer", parent=answer)


@pytest.fixture
def child_answer_of_same_user(answer, question, mixer, api):
    return mixer.blend("homework.Answer", question=question, parent=answer, author=api.user)


@pytest.fixture
def purchase(factory, course, api):
    order = factory.order(user=api.user, item=course)
    order.set_paid()

    return order


@pytest.fixture
def purchase_of_another_course(factory, another_course, api):
    order = factory.order(user=api.user, item=another_course)
    order.set_paid()

    return order


@pytest.fixture
def _no_purchase(purchase, purchase_of_another_course, _set_current_user):
    """Invalidate the purchase"""
    purchase.refund(amount=purchase.price)
    purchase_of_another_course.refund(amount=purchase_of_another_course.price)


@pytest.fixture
def emoji():
    return "🐍"


@pytest.fixture
def reaction(mixer, answer, api, emoji):
    return mixer.blend("homework.Reaction", answer=answer, author=api.user, emoji=emoji)
