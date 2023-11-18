import pytest

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def send_mail(mocker):
    return mocker.patch("apps.mailing.tasks.send_mail.delay")


@pytest.fixture(autouse=True)
def _freeze_frontend_host(settings):
    settings.FRONTEND_URL = "https://school.host"


def test_message_is_not_sent_by_default(create, user, course, send_mail):
    create(user=user, item=course)

    send_mail.assert_not_called()


def test_message_is_not_sent_on_non_free_courses(create, user, course, send_mail):
    course.update(
        confirmation_template_id="test-confirmation-template-id",
        price=100500,
    )

    send_mail.assert_not_called()


def test_message_is_sent_when_course_has_confirmation_template_id(create, user, course, send_mail):
    course.update(
        confirmation_template_id="test-confirmation-template-id",
        price=0,
    )

    order = create(user=user, item=course)

    send_mail.assert_called_once_with(
        to=user.email,
        template_id="test-confirmation-template-id",
        ctx=dict(
            item="Курс кройки и шитья",
            item_lower="курс кройки и шитья",
            firstname="Авраам Соломонович",
            confirmation_url=f"https://school.host/api/v2/orders/{order.slug}/confirm/",
        ),
    )
