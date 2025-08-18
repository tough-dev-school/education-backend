import pytest

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def question(factory):
    question = factory.question(name="Девятнадцатая домашка")

    return question


@pytest.fixture
def module(factory, course):
    return factory.module(course=course)


@pytest.fixture
def user(mixer):
    return mixer.blend("users.User", is_superuser=False)


@pytest.fixture(autouse=True)
def lesson(factory, module, question):
    return factory.lesson(module=module, question=question)


@pytest.fixture(autouse=True)
def purchase(factory, user, course):
    return factory.order(item=course, user=user, is_paid=True)


@pytest.fixture
def _no_purchase(purchase):
    purchase.unship()


@pytest.fixture
def another_course(factory):
    return factory.course(name="Другойкурсология для 11 класса")


def test_no_lesson(question, lesson, user):
    lesson.update(question=None)

    assert question.get_lesson(user=user) is None


@pytest.mark.usefixtures("_no_purchase")
def test_no_purchase(question, user):
    assert question.get_lesson(user=user) is None


@pytest.mark.usefixtures("_no_purchase", "another_course")
def test_not_attached_courses_do_not_appear_in_the_breadcrumbs(question, user):
    assert question.get_lesson(user=user) is None


def test_ok(question, lesson, user):
    assert question.get_lesson(user=user) == lesson


@pytest.mark.usefixtures("_no_purchase")
def test_user_with_permission_sees_all_courses(question, lesson, user):
    user.add_perm("studying.study.purchased_all_courses")

    assert question.get_lesson(user=user) == lesson
