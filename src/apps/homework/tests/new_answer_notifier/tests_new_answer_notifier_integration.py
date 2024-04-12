import pytest

from apps.homework.models import Answer

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def commenter(mixer):
    return mixer.blend("users.User")


@pytest.fixture(autouse=True)
def _enable_new_answer_notification(settings):
    settings.DISABLE_NEW_ANSWER_NOTIFICATIONS = False


@pytest.fixture
def get_notified_users(send_mail):
    return lambda: [call.kwargs["to"] for call in send_mail.mock_calls]


@pytest.fixture
def reply(api):
    def _reply(answer, payload, as_user=None):
        if as_user is not None:
            api.auth(as_user)
        return api.post(
            "/api/v2/homework/answers/",
            {
                "question": answer.question.slug,
                "parent": answer.slug,
                **payload,
            },
        )

    return _reply


def test_notifying_author(reply, answer, get_notified_users):
    reply(
        answer,
        {
            "text": "Верните деньги!",
        },
    )

    assert get_notified_users() == [answer.author.email]


def test_not_notifying_commenter(reply, answer, commenter, get_notified_users):
    reply(
        answer,
        {
            "text": "Верните деньги!",
        },
        as_user=commenter,
    )

    assert commenter.email not in get_notified_users()


def test_notifying_another_commenter(reply, answer, another_user, commenter, get_notified_users):
    reply(
        answer,
        {
            "text": "Верните деньги!",
        },
        as_user=commenter,
    )

    reply(
        answer,
        {
            "text": "Мне тоже!",
        },
        as_user=another_user,
    )

    assert set(get_notified_users()) == {answer.author.email, answer.author.email, commenter.email}


def test_disabling_feature_disables_sending(reply, answer, settings, get_notified_users):
    settings.DISABLE_NEW_ANSWER_NOTIFICATIONS = True

    reply(
        answer,
        {
            "text": "Верните деньги!",
        },
    )

    assert get_notified_users() == []


def test_editing_answer_does_not_send_email_for_the_second_time(reply, answer, get_notified_users):
    reply(
        answer,
        {
            "text": "Верните деньги!",
        },
    )

    Answer.objects.order_by("-id").first().save()  # we do not have an endpoint for that so calling .save() directly

    assert get_notified_users() == [answer.author.email]
