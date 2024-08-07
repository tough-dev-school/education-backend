import pytest

from apps.homework import tasks
from apps.homework.models import AnswerCrossCheck

pytestmark = [pytest.mark.django_db]


def test_crosschecks_are_created(question_dispatcher):
    question_dispatcher()

    assert AnswerCrossCheck.objects.count() == 2


def test_question_method_does_the_same(question):
    question.dispatch_crosscheck(answers_per_user=1)

    assert AnswerCrossCheck.objects.count() == 2


def test_task_does_the_same(question):
    tasks.dispatch_crosscheck.delay(question_id=question.pk, answers_per_user=1)

    assert AnswerCrossCheck.objects.count() == 2


def test_email_is_sent(question_dispatcher, send_mail, mocker, answers):
    question_dispatcher()

    assert send_mail.call_count == 2
    send_mail.assert_has_calls(
        [
            mocker.call(
                to=answers[0].author.email,
                template_id="new-answers-to-check",
                disable_antispam=True,
                ctx={
                    "answers": [
                        {
                            "url": mocker.ANY,
                            "text": mocker.ANY,
                        },
                    ],
                },
            ),
        ]
    )
