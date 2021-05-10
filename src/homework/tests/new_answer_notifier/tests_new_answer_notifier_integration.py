import pytest

from homework.models import Answer

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def _enable_new_answer_notification(settings):
    settings.DISABLE_NEW_ANSWER_NOTIFICATIONS = False


def test_notifying_author(api, answer, send_mail, mocker):
    api.post('/api/v2/homework/answers/', {
        'question': answer.question.slug,
        'parent': answer.slug,
        'text': 'Верните деньги!',
    })

    send_mail.assert_called_once_with(
        to=answer.author.email,
        template_id='new-answer-notification',
        ctx=mocker.ANY,
        disable_antispam=True,
    )


def test_disabling_feature_disable_sending(api, settings, answer, send_mail):
    settings.DISABLE_NEW_ANSWER_NOTIFICATIONS = True

    api.post('/api/v2/homework/answers/', {
        'question': answer.question.slug,
        'parent': answer.slug,
        'text': 'Верните деньги!',
    })

    send_mail.assert_not_called()


def test_editing_answer_does_not_send_email_for_the_second_time(api, answer, send_mail):
    api.post('/api/v2/homework/answers/', {
        'question': answer.question.slug,
        'parent': answer.slug,
        'text': 'Верните деньги!',
    })

    Answer.objects.order_by('-id').first().save()  # we do not have an endpoint for that yet, sorry

    send_mail.assert_called_once()
