import pytest
from django.utils import timezone

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("answer"),
]


@pytest.fixture
def comments(answer, mixer, another_user):
    return mixer.cycle(2).blend("homework.Answer", parent=answer, question=answer.question, author=another_user)


@pytest.fixture
def crosscheck_that_user_should_perform(mixer, answer):
    return mixer.blend(
        "homework.AnswerCrossCheck",
        checker=answer.author,
        answer=mixer.blend("homework.Answer", question=answer.question),
        checked=None,
    )


@pytest.fixture
def one_more_crosscheck_that_user_should_perform(mixer, answer):
    return mixer.blend(
        "homework.AnswerCrossCheck",
        checker=answer.author,
        answer=mixer.blend("homework.Answer", question=answer.question),
        checked=None,
    )


@pytest.fixture
def crosscheck_that_user_should_recieve(mixer, answer, another_user):
    return mixer.blend(
        "homework.AnswerCrossCheck",
        checker=another_user,
        answer=answer,
        checked=None,
    )


@pytest.fixture
def crosschecks(crosscheck_that_user_should_recieve, crosscheck_that_user_should_perform):
    return {
        "recieved": crosscheck_that_user_should_recieve,
        "to_perform": crosscheck_that_user_should_perform,
    }


def test_no_answer(api, module, answer):
    answer.delete()

    got = api.get(f"/api/v2/lms/lessons/?module={module.pk}")

    assert got["results"][0]["homework"]["comments"] == {}


def test_two_root_answers(api, module, answer, mixer):
    """Addresses a bug from https://app.glitchtip.com/tough-dev-school/issues/2972425"""
    mixer.blend("homework.Answer", author=api.user, question=answer.question, parent=None)

    got = api.get(f"/api/v2/lms/lessons/?module={module.pk}")

    assert len(got["results"]) == 1


def test_no_comments(api, module):
    got = api.get(f"/api/v2/lms/lessons/?module={module.pk}")

    assert got["results"][0]["homework"]["comments"] == {
        "comments": 0,
        "hidden_before_crosscheck_completed": 0,
    }


@pytest.mark.usefixtures("comments")
def test_crosscheck_is_not_dispatched(api, module):
    got = api.get(f"/api/v2/lms/lessons/?module={module.pk}")

    assert got["results"][0]["homework"]["comments"] == {
        "comments": 2,
        "hidden_before_crosscheck_completed": 0,
    }


def test_own_comments_are_ignored(api, module, comments):
    for comment in comments:
        comment.update(author=api.user)

    got = api.get(f"/api/v2/lms/lessons/?module={module.pk}")

    assert got["results"][0]["homework"]["comments"]["comments"] == 0


def test_comments_from_another_questions_are_ignored(api, module, comments, mixer):
    another_question = mixer.blend("homework.Question", course=module.course)
    another_answer = mixer.blend("homework.Answer", author=api.user, question=another_question)
    for comment in comments:
        comment.update(question=another_question, parent=another_answer)

    got = api.get(f"/api/v2/lms/lessons/?module={module.pk}")

    assert got["results"][0]["homework"]["comments"]["comments"] == 0


@pytest.mark.usefixtures("comments", "crosschecks")
def test_crosscheck_is_dispatched(api, module):
    got = api.get(f"/api/v2/lms/lessons/?module={module.pk}")

    assert got["results"][0]["homework"]["comments"] == {
        "comments": 2,
        "hidden_before_crosscheck_completed": 2,
    }


@pytest.mark.usefixtures("comments")
def test_all_crosschecks_are_performed(api, module, crosschecks):
    crosschecks["to_perform"].update(checked=timezone.now())

    got = api.get(f"/api/v2/lms/lessons/?module={module.pk}")

    assert got["results"][0]["homework"]["comments"] == {
        "comments": 2,
        "hidden_before_crosscheck_completed": 0,  # should be zero cuz user have done all the checks
    }


@pytest.mark.usefixtures("comments", "crosschecks", "one_more_crosscheck_that_user_should_perform")
def test_only_one_crosscheck_is_performed(api, module, crosschecks):
    crosschecks["to_perform"].update(checked=timezone.now())  # check only one crosscheck, leaving the second one unchecked

    got = api.get(f"/api/v2/lms/lessons/?module={module.pk}")

    assert got["results"][0]["homework"]["comments"] == {
        "comments": 2,
        "hidden_before_crosscheck_completed": 1,
    }


@pytest.mark.usefixtures("comments", "crosschecks")
@pytest.mark.parametrize("perm", ["homework.answer.see_all_answers", "studying.study.purchased_all_courses"])
def test_does_not_die_for_user_with_permissions(api, module, answer, another_user, perm):
    answer.update(author=another_user)
    api.user.add_perm(perm)

    got = api.get(f"/api/v2/lms/lessons/?module={module.pk}")

    assert got["results"][0]["homework"]["comments"] == {}
