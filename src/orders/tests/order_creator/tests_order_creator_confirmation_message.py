import pytest

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def send_mail(mocker):
    return mocker.patch('mailing.tasks.send_mail.delay')


def test_message_is_not_sent_by_default(create, user, course, send_mail):
    create(user=user, item=course)

    send_mail.assert_not_called()


def test_message_is_not_sent_on_non_free_courses(create, user, course, send_mail):
    course.update_from_kwargs(
        confirmation_template_id='test-confirmation-template-id',
        price=100500,
    )

    send_mail.assert_not_called()


def test_message_is_sent_when_course_has_confirmation_template_id(create, user, course, send_mail):
    course.update_from_kwargs(
        confirmation_template_id='test-confirmation-template-id',
        price=0,
    )

    create(user=user, item=course)

    send_mail.assert_called_once_with(
        to=user.email,
        template_id='test-confirmation-template-id',
        ctx=dict(
            item='Курс кройки и шитья',
            item_lower='курс кройки и шитья',
            firstname='Авраам Соломонович',
        ),
    )
