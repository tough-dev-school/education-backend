import pytest

from orders import tasks
from orders.services import OrderDiplomaGenerator

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def student(mixer):
    return mixer.blend('users.User', first_name='Омон', last_name='Кривомазов', gender='male')


@pytest.fixture
def course(mixer):
    return mixer.blend('products.Course')


@pytest.fixture
def order(factory, course, student):
    return factory.order(user=student, item=course, is_paid=True)


@pytest.fixture(autouse=True)
def template(mixer, course):
    return mixer.blend('diplomas.DiplomaTemplate', slug='test-template', course=course, language='ru', homework_accepted=False)


@pytest.fixture
def diploma_generator(mocker):
    return mocker.patch('orders.services.order_diploma_generator.generate_diploma.delay')


@pytest.mark.parametrize('language', ['ru', 'en'])
def test_single_language(diploma_generator, order, student, course, template, language):
    template.language = language
    template.save()

    OrderDiplomaGenerator(order=order)()

    diploma_generator.assert_called_once_with(
        student=student,
        course=course,
        language=language,
    )


def test_task(diploma_generator, order, student, course):
    tasks.generate_diploma.delay(order_id=order.id)

    diploma_generator.assert_called_once_with(
        student=student,
        course=course,
        language='ru',
    )


@pytest.mark.parametrize('name_field', ['first_name', 'last_name'])
def test_student_without_name_does_not_get_a_diploma(diploma_generator, order, student, name_field):
    setattr(student, name_field, '')  # reset a part of students name
    student.save()

    tasks.generate_diploma.delay(order_id=order.id)

    diploma_generator.assert_not_called()
