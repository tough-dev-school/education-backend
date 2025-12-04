import pytest

from apps.homework import tasks
from apps.homework.models import AnswerCrossCheck

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def common_group_for_both_courses(course, another_course, mixer):
    group = mixer.blend("products.Group")

    course.update(group=group)
    another_course.update(group=group)

    return group


def test_crosschecks_are_created(question_dispatcher):
    question_dispatcher()

    assert AnswerCrossCheck.objects.count() == 2


@pytest.mark.usefixtures("answers_to_another_question")
def test_answers_to_another_questions_are_ignored(question_dispatcher, question, another_question):
    first_question_course = question.lesson_set.first().module.course
    second_question_course = another_question.lesson_set.first().module.course
    assert first_question_course != second_question_course, "Questions are attached to the different courses"
    assert first_question_course.group == second_question_course.group, "Courses have the same group"

    question_dispatcher()

    assert AnswerCrossCheck.objects.count() == 2


@pytest.mark.usefixtures("answers_to_another_question")
def test_answers_to_another_questions_are_dispatched_if_product_and_name_match(question, another_question, question_dispatcher):
    question.update(name="Одинаковая домаЩка")  # also check case insensitiviy
    another_question.update(name="Одинаковая домащка")

    question_dispatcher()

    assert AnswerCrossCheck.objects.count() == 4


@pytest.mark.usefixtures("answers_to_another_question")
def test_anothers_to_another_questions_are_not_dispatched_if_name_matches_but_product_does_not(question, another_question, question_dispatcher, mixer):
    """Same as above, but changing product group of one of the courses"""
    question.update(name="Одинаковая домаЩка")
    another_question.update(name="Одинаковая домащка")

    question.lesson_set.first().module.course.update(group=mixer.blend("products.Group"))  # this removes 2 questions from the crosscheck

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


def test_answer_text(question_dispatcher, send_mail, answers):
    answers[0].update(legacy_text="Ссылка на members-x.com")

    question_dispatcher()

    for call in send_mail.call_args_list:  # find the answer with updated_id
        template_context = call.kwargs["ctx"]
        if str(answers[0].slug) in template_context["answers"][0]["url"]:
            assert "Ссылка на members-x.com" in template_context["answers"][0]["text"]

            return

    pytest.fail("Answer not found")


def test_empty_answer_text(question_dispatcher, send_mail, answers):
    """Template should not fail if answer has empty text"""
    answers[0].update(legacy_text="")

    question_dispatcher()

    for call in send_mail.call_args_list:  # find the answer with updated_id
        template_context = call.kwargs["ctx"]
        if str(answers[0].slug) in template_context["answers"][0]["url"]:
            assert template_context["answers"][0]["text"] == answers[0].get_absolute_url()  # should be a link instead of text if text is empty

            return

    pytest.fail("Answer not found")
