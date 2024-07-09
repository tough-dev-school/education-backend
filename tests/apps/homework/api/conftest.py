import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def api(api):
    """We test it as normal student, not superuser to check permissions"""
    api.user.update(is_superuser=False)

    return api


@pytest.fixture
def ya_user(mixer):
    return mixer.blend("users.User")


@pytest.fixture
def question(mixer, course):
    question = mixer.blend("homework.Question")
    question.courses.add(course)

    return question


@pytest.fixture
def another_question(mixer, course):
    another_question = mixer.blend("homework.Question")
    another_question.courses.add(course)

    return another_question


@pytest.fixture
def answer(mixer, question, api):
    return mixer.blend("homework.Answer", question=question, author=api.user, text="*test*")


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
def _no_purchase(purchase):
    """Invalidate the purchase"""
    purchase.update(paid=None)


@pytest.fixture
def emoji():
    return "🐍"


@pytest.fixture
def reaction(mixer, answer, api, emoji):
    return mixer.blend("homework.Reaction", answer=answer, author=api.user, emoji=emoji)
